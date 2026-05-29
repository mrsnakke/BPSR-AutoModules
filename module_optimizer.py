# module_optimizer.py

import logging
import os
import random
import math
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from copy import deepcopy
from concurrent.futures import ProcessPoolExecutor, as_completed

from logging_config import get_logger
from module_types import (
    ModuleInfo, ModuleType, ModuleAttrType, ModuleCategory,
    MODULE_CATEGORY_MAP, ATTR_THRESHOLDS, BASIC_ATTR_POWER_MAP, SPECIAL_ATTR_POWER_MAP,
    TOTAL_ATTR_POWER_MAP, BASIC_ATTR_IDS, SPECIAL_ATTR_IDS, ATTR_NAME_TYPE_MAP
)

# Get logger
logger = get_logger(__name__)

# --- Attribute Category Definitions (unchanged) ---
PHYSICAL_ATTRIBUTES = {"Strength Boost", "Agility Boost", "Attack SPD"}
MAGIC_ATTRIBUTES = {"Intellect Boost", "Cast Focus"}
ATTACK_ATTRIBUTES = {"Special Attack", "Elite Strike", "Strength Boost", "Agility Boost", "Intellect Boost"}
GUARDIAN_ATTRIBUTES = {"Resistance", "Armor"}
SUPPORT_ATTRIBUTES = {"Healing Boost", "Healing Enhance"}

MODULE_COMBINATION_SIZE = 5
ENABLE_FITNESS_CACHE = True
GLOBAL_FITNESS_CACHE: Dict[Tuple[int, ...], float] = {}

# --- Solution Data Class (unchanged) ---
@dataclass
class ModuleSolution:
    """Represents a module combination solution."""
    modules: List[ModuleInfo]
    attr_breakdown: Dict[str, int] = field(default_factory=dict)
    score: float = 0.0  # Final combat power
    optimization_score: float = 0.0 # Fitness score used during optimization

    def __post_init__(self):
        self.modules.sort(key=lambda m: m.uuid)

    def get_combination_id(self) -> Tuple[str, ...]:
        return tuple(m.uuid for m in self.modules)

# --- Top-level functions for parallel execution ---
# These functions are defined at the top level so they can be "pickled" by the multiprocessing module.

def calculate_fitness(modules: List[ModuleInfo], category: ModuleCategory,
                      prioritized_attrs: Optional[List[str]] = None,
                      cache: Optional[Dict[Tuple[int, ...], float]] = None) -> float:
    """Independent fitness calculation function."""
    if not modules or len(set(m.uuid for m in modules)) < MODULE_COMBINATION_SIZE: return 0.0
    combo_key = tuple(sorted(m.uuid for m in modules))
    if cache is None and ENABLE_FITNESS_CACHE:
        cache = GLOBAL_FITNESS_CACHE
    if cache is not None and combo_key in cache:
        return cache[combo_key]

    attr_breakdown = {}
    for module in modules:
        for part in module.parts:
            attr_breakdown[part.name] = attr_breakdown.get(part.name, 0) + part.value
    
    score = 0.0

    # Helper to convert value -> level (0..6)
    def value_to_level_fitness(val: int) -> int:
        if val >= 20: return 6
        if val >= 16: return 5
        if val >= 12: return 4
        if val >= 8: return 3
        if val >= 4: return 2
        if val >= 1: return 1
        return 0

    if prioritized_attrs:
        prioritized_set = set(prioritized_attrs)
        # Give strong bonus for prioritized attributes, especially at higher levels
        prioritized_attr_score = 0
        for attr_name in prioritized_attrs:
            value = attr_breakdown.get(attr_name, 0)
            level = value_to_level_fitness(value)
            if level == 6: prioritized_attr_score += 5000 # Very strong bonus for Lv6
            elif level == 5: prioritized_attr_score += 2000 # Strong bonus for Lv5
            elif level == 4: prioritized_attr_score += 500
            elif level == 3: prioritized_attr_score += 100
            elif level == 2: prioritized_attr_score += 50
            elif level == 1: prioritized_attr_score += 10
        score += prioritized_attr_score

        # Also give a general bonus for just having prioritized attributes
        match_count = len(prioritized_set.intersection(set(attr_breakdown.keys())))
        score += match_count * 100 # Keep a smaller bonus for presence

        # Minor penalty for non-prioritized attributes if prioritized_attrs is active
        # This helps prune solutions that are "too wide" when only specific attributes matter
        if prioritized_set: # Only apply if there are actual prioritized attrs
            non_prioritized_attrs = set(attr_breakdown.keys()).difference(prioritized_set)
            score -= sum(attr_breakdown[attr] for attr in non_prioritized_attrs) * 5 # Small penalty for other attributes


    threshold_score = 0
    for attr_name, value in attr_breakdown.items():
        if value >= 20: threshold_score += 1000 + (value - 20) * 20
        elif value >= 16: threshold_score += 500 + (value - 16) * 15
        elif value >= 12: threshold_score += 100 + (value - 12) * 5
    score += threshold_score

    target_attrs = set()
    if category == ModuleCategory.ATTACK: target_attrs = ATTACK_ATTRIBUTES
    elif category == ModuleCategory.GUARDIAN: target_attrs = GUARDIAN_ATTRIBUTES
    elif category == ModuleCategory.SUPPORT: target_attrs = SUPPORT_ATTRIBUTES
    score += sum(value * 5 for attr_name, value in attr_breakdown.items() if attr_name in target_attrs)

    physical_sum = sum(v for k, v in attr_breakdown.items() if k in PHYSICAL_ATTRIBUTES)
    magic_sum = sum(v for k, v in attr_breakdown.items() if k in MAGIC_ATTRIBUTES)
    if physical_sum > 0 and magic_sum > 0:
        score -= min(physical_sum, magic_sum) * 10

    score += sum(attr_breakdown.values()) * 0.1
    return max(0.0, score)

def run_single_ga_campaign(
    modules: List[ModuleInfo],
    category: ModuleCategory,
    prioritized_attrs: Optional[List[str]],
    ga_params: Dict
) -> List[ModuleSolution]:
    """
    执行一次完整的遗传算法流程。这是单个进程工作单元的目标函数。
    """
    fitness_cache: Dict[Tuple[int, ...], float] = {} if ENABLE_FITNESS_CACHE else {}
    # 辅助函数嵌套在这里，不需要被序列化
    def _initialize_population(pool, size):
        population, seen = [], set()
        if len(pool) < MODULE_COMBINATION_SIZE: return []
        try:
            max_possible_combinations = math.comb(len(pool), MODULE_COMBINATION_SIZE)
        except AttributeError:
            def combinations(n, k):
                if k < 0 or k > n: return 0
                if k == 0 or k == n: return 1
                if k > n // 2: k = n - k
                res = 1
                for i in range(k):
                    res = res * (n - i) // (i + 1)
                return res
            max_possible_combinations = combinations(len(pool), MODULE_COMBINATION_SIZE)
        target_size = min(size, max_possible_combinations)
        if target_size == 0: return []
        while len(population) < target_size:
            selected_modules = random.sample(pool, MODULE_COMBINATION_SIZE)
            solution = ModuleSolution(modules=selected_modules)
            combo_id = solution.get_combination_id()
            if combo_id not in seen:
                solution.optimization_score = calculate_fitness(solution.modules, category, prioritized_attrs,
                                                               cache=fitness_cache if ENABLE_FITNESS_CACHE else None)
                population.append(solution)
                seen.add(combo_id)
        return population
 
    def _selection(population):
        tournament = random.sample(population, ga_params['tournament_size'])
        return max(tournament, key=lambda s: s.optimization_score)

    def _crossover(p1, p2):
        if random.random() > ga_params['crossover_rate']: return deepcopy(p1), deepcopy(p2)
        split = MODULE_COMBINATION_SIZE // 2 + MODULE_COMBINATION_SIZE % 2
        child1_mods = p1.modules[:split] + [m for m in p2.modules if m.uuid not in {mod.uuid for mod in p1.modules[:split]}][:MODULE_COMBINATION_SIZE - split]
        child2_mods = p2.modules[:split] + [m for m in p1.modules if m.uuid not in {mod.uuid for mod in p2.modules[:split]}][:MODULE_COMBINATION_SIZE - split]
        return (ModuleSolution(modules=child1_mods) if len(child1_mods) == MODULE_COMBINATION_SIZE else deepcopy(p1),
                ModuleSolution(modules=child2_mods) if len(child2_mods) == MODULE_COMBINATION_SIZE else deepcopy(p2))

    def _mutate(solution, pool):
        if random.random() > ga_params['mutation_rate']: return
        current_ids = {m.uuid for m in solution.modules}
        candidates = [m for m in pool if m.uuid not in current_ids]
        if not candidates: return
        index_to_replace = random.randrange(len(solution.modules))
        solution.modules[index_to_replace] = random.choice(candidates)
        solution.modules.sort(key=lambda m: m.uuid)

    def _local_search(solution, pool):
        best_solution = deepcopy(solution)
        while True:
            improved = False
            for i in range(len(best_solution.modules)):
                current_module = best_solution.modules[i]
                best_replacement = None
                best_new_score = best_solution.optimization_score
                occupied_ids = {m.uuid for m in best_solution.modules if m.uuid != current_module.uuid}
                for new_module in pool:
                    if new_module.uuid in occupied_ids: continue
                    temp_modules = best_solution.modules[:i] + [new_module] + best_solution.modules[i+1:]
                    new_score = calculate_fitness(temp_modules, category, prioritized_attrs,
                                                  cache=fitness_cache if ENABLE_FITNESS_CACHE else None)
                    if new_score > best_new_score:
                        best_new_score = new_score
                        best_replacement = new_module
                if best_replacement:
                    best_solution.modules[i] = best_replacement
                    best_solution.optimization_score = best_new_score
                    best_solution.modules.sort(key=lambda m: m.uuid)
                    improved = True
            if not improved: break
        return best_solution
    
    population = _initialize_population(modules, ga_params['population_size'])
    if not population: return []
    for _ in range(ga_params['generations']):
        population.sort(key=lambda s: s.optimization_score, reverse=True)
        next_gen, elite_count = [], int(ga_params['population_size'] * ga_params['elitism_rate'])
        next_gen.extend(deepcopy(population[:elite_count]))
        while len(next_gen) < ga_params['population_size']:
            p1, p2 = _selection(population), _selection(population)
            c1, c2 = _crossover(p1, p2)
            _mutate(c1, modules); _mutate(c2, modules)
            next_gen.extend([c1, c2])
        for individual in next_gen:
            individual.optimization_score = calculate_fitness(individual.modules, category, prioritized_attrs,
                                                            cache=fitness_cache if ENABLE_FITNESS_CACHE else None)
        next_gen.sort(key=lambda s: s.optimization_score, reverse=True)
        local_search_count = int(ga_params['population_size'] * ga_params['local_search_rate'])
        for i in range(local_search_count):
            next_gen[i] = _local_search(next_gen[i], modules)
        population = next_gen
    return sorted(population, key=lambda s: s.optimization_score, reverse=True)


class ModuleOptimizer:
    """
    使用并行的多轮遗传算法来寻找最优模组组合。
    """

    def __init__(self):
        self.logger = logger
        self._result_log_file = None
        self.ga_params = {
            'population_size': 150, 'generations': 50, 'mutation_rate': 0.1,
            'crossover_rate': 0.8, 'elitism_rate': 0.1, 'tournament_size': 5,
            'local_search_rate': 0.3,
        }
        self.num_campaigns = max(1, os.cpu_count() - 1)
        self.quality_threshold = 12
        self.prefilter_top_n_per_attr = 60
        self.prefilter_top_n_total_value = 100

    def _get_current_log_file(self) -> Optional[str]:
        try:
            root_logger = logging.getLogger()
            for handler in root_logger.handlers:
                if isinstance(handler, logging.FileHandler): return handler.baseFilename
            return None
        except Exception as e:
            self.logger.warning(f"无法获取日志文件路径: {e}")
            return None

    def _log_result(self, message: str):
        try:
            if self._result_log_file is None: self._result_log_file = self._get_current_log_file()
            if self._result_log_file and os.path.exists(self._result_log_file):
                with open(self._result_log_file, 'a', encoding='utf-8') as f:
                    f.write(message + '\n')
        except Exception as e:
            self.logger.warning(f"记录筛选结果失败: {e}")

    def get_module_category(self, module: ModuleInfo) -> ModuleCategory:
        return MODULE_CATEGORY_MAP.get(module.config_id, ModuleCategory.ATTACK)

    def prefilter_modules(self, modules: List[ModuleInfo], prioritized_attrs: Optional[List[str]] = None) -> List[ModuleInfo]:
        self.logger.info(f"Starting pre-filtering, original number of modules: {len(modules)}")
        if not modules:
            return []

        # First, filter by total attribute value to get a base set of high-quality modules
        sorted_by_total_value = sorted(modules, key=lambda m: sum(p.value for p in m.parts), reverse=True)
        top_modules = set(sorted_by_total_value[:self.prefilter_top_n_total_value])

        # Then, get the top modules for each attribute
        attr_modules = {p.name: [] for m in modules for p in m.parts}
        for module in modules:
            for part in module.parts:
                attr_modules[part.name].append((module, part.value))

        candidate_modules = set(top_modules)
        for attr_name, module_values in attr_modules.items():
            # If prioritized_attrs is specified, only consider those attributes for this part of the filtering
            if prioritized_attrs and attr_name not in prioritized_attrs:
                continue
            sorted_by_attr = sorted(module_values, key=lambda x: x[1], reverse=True)
            candidate_modules.update(item[0] for item in sorted_by_attr[:self.prefilter_top_n_per_attr])

        filtered_modules = list(candidate_modules)
        self.logger.info(f"Pre-filtering complete, candidate pool size: {len(filtered_modules)}")
        return filtered_modules

    # --- CORRECTED METHOD ---
    def calculate_combat_power(self, modules: List[ModuleInfo]) -> Tuple[int, Dict[str, int]]:
        """
        修正后的战斗力计算方法。
        """
        attr_breakdown = {}
        # 先初始化字典，再遍历模组进行累加
        for module in modules:
            for part in module.parts:
                attr_breakdown[part.name] = attr_breakdown.get(part.name, 0) + part.value
        
        threshold_power, total_attr_value = 0, sum(attr_breakdown.values())
        for attr_name, attr_value in attr_breakdown.items():
            max_level = sum(1 for threshold in ATTR_THRESHOLDS if attr_value >= threshold)
            if max_level > 0:
                attr_type = ATTR_NAME_TYPE_MAP.get(attr_name, "basic")
                power_map = SPECIAL_ATTR_POWER_MAP if attr_type == 'special' else BASIC_ATTR_POWER_MAP
                threshold_power += power_map.get(max_level, 0)
        
        total_attr_power = TOTAL_ATTR_POWER_MAP.get(total_attr_value, 0)
        return threshold_power + total_attr_power, attr_breakdown
    # --- END OF CORRECTION ---

    def _preliminary_check(self, module_pool: List[ModuleInfo], prioritized_attrs: Optional[List[str]]) -> bool:
        if not prioritized_attrs: return True
        available_attrs = {p.name for m in module_pool for p in m.parts}
        prioritized_set = set(prioritized_attrs)
        intersection = available_attrs.intersection(prioritized_set)
        if len(intersection) == 0:
            self.logger.warning("="*50 + "\n>>> Pre-check failed: Filtering cannot proceed!\n" +
                                f">>> Reason: No user-specified prioritized attributes found in the selected module type.\n" +
                                f">>> Optimization skipped automatically. Please adjust module types or filter attributes and retry.\n" + "="*50)
            return False
        # Allow optimization to proceed with at least one prioritized attribute
        return True

    def _get_attribute_level_key(self, attr_breakdown: Dict[str, int]) -> Tuple[str, ...]:
        """Calculates a unique key for deduplication based on attribute levels from the attribute breakdown."""
        levels = []
        for attr_name, value in sorted(attr_breakdown.items()):
            level_str = "(Level 0)"
            if value >= 20: level_str = "(Level 6)"
            elif value >= 16: level_str = "(Level 5)"
            elif value >= 12: level_str = "(Level 4)"
            elif value >= 8: level_str = "(Level 3)"
            elif value >= 4: level_str = "(Level 2)"
            elif value >= 1: level_str = "(Level 1)"
            levels.append(f"{attr_name}{level_str}")
        return tuple(levels)

    def _compute_priority_sort_key(self, solution: ModuleSolution, prioritized_attrs: List[str], top_k: int = 4) -> Tuple:
        """Compute a sort key for a solution based on prioritized attributes.

        The key orders solutions by counts of highest levels among the top_k prioritized attributes.
        Returned tuple is suitable for sorting in descending order.
        """
        # helper to convert value -> level (0..6) using same thresholds as elsewhere
        def value_to_level(val: int) -> int:
            if val >= 20: return 6
            if val >= 16: return 5
            if val >= 12: return 4
            if val >= 8: return 3
            if val >= 4: return 2
            if val >= 1: return 1
            return 0

        # build list of (attr_name, level, user_index)
        levels = []
        for idx, attr in enumerate(prioritized_attrs):
            lvl = value_to_level(solution.attr_breakdown.get(attr, 0))
            levels.append((attr, lvl, idx))

        # pick top_k attributes by (level desc, user order asc)
        top_selected = sorted(levels, key=lambda x: (-x[1], x[2]))[:top_k]

        # count occurrences of each high level (6..1)
        counts = {i: 0 for i in range(1, 7)}
        sum_levels = 0
        for _attr, lvl, _ in top_selected:
            if lvl >= 1:
                counts[lvl] += 1
                sum_levels += lvl

        # build key: prefer more 6s, then 5s, then 4s, ..., then sum_levels, then score, then optimization_score
        key = (
            counts[6], counts[5], counts[4], counts[3], counts[2], counts[1],
            sum_levels,
            solution.score if solution.score is not None else 0,
            solution.optimization_score if solution.optimization_score is not None else 0
        )
        return key

    def optimize_modules(self, modules: List[ModuleInfo], category: ModuleCategory, top_n: int = 40,
                         prioritized_attrs: Optional[List[str]] = None,
                         priority_order_mode: bool = False,
                         progress_callback: Optional[Callable[[str], None]] = None) -> List[ModuleSolution]:
        
        self.logger.info(f"Starting optimization for {category.value} type modules (using {self.num_campaigns} parallel tasks)")
        module_pool = modules if category == ModuleCategory.All else [m for m in modules if self.get_module_category(m) == category]
        
        if prioritized_attrs:
            self.logger.info(f"Applying inclusive filtering: keeping modules that have at least one of the desired attributes: {prioritized_attrs}.")
            original_count = len(module_pool)
            prioritized_set = set(prioritized_attrs)
            module_pool = [m for m in module_pool if any(p.name in prioritized_set for p in m.parts)]
            self.logger.info(f"Inclusive filtering completed: module count reduced from {original_count} to {len(module_pool)}.")

        if not self._preliminary_check(module_pool, prioritized_attrs): return []
        candidate_modules = self.prefilter_modules(module_pool, prioritized_attrs)
        if len(candidate_modules) < MODULE_COMBINATION_SIZE:
            self.logger.warning(f"Less than {MODULE_COMBINATION_SIZE} modules after pre-filtering, unable to form valid combinations.")
            return []

        high_quality_modules = [m for m in candidate_modules if sum(p.value for p in m.parts) >= self.quality_threshold]
        low_quality_modules = [m for m in candidate_modules if sum(p.value for p in m.parts) < self.quality_threshold]
        self.logger.info(f"Module pooling completed: {len(high_quality_modules)} high-quality modules, {len(low_quality_modules)} low-quality modules.")
        if len(high_quality_modules) < MODULE_COMBINATION_SIZE:
            self.logger.warning(f"Less than {MODULE_COMBINATION_SIZE} high-quality modules, using all candidate modules for optimization.")
            high_quality_modules = candidate_modules
            low_quality_modules = []

        all_best_solutions = []
        with ProcessPoolExecutor(max_workers=self.num_campaigns) as executor:
            self.logger.info(f"--- Phase One: Running {self.num_campaigns} GA campaigns in parallel on the high-quality module pool ---")
            if progress_callback: progress_callback(f"Running {self.num_campaigns} parallel optimization tasks...")
            futures = [executor.submit(run_single_ga_campaign, high_quality_modules, category, prioritized_attrs, self.ga_params)
                       for _ in range(self.num_campaigns)]
            for i, future in enumerate(as_completed(futures)):
                try:
                    campaign_results = future.result()
                    if campaign_results:
                        all_best_solutions.extend(campaign_results)
                        best_score = campaign_results[0].optimization_score
                        self.logger.info(f"Task {i+1}/{self.num_campaigns} completed. Highest fitness: {best_score:.2f}")
                        if progress_callback: progress_callback(f"Task {i+1}/{self.num_campaigns} completed. Highest score: {best_score:.2f}")
                except Exception as e:
                    self.logger.error(f"An optimization task failed: {e}")

        self.logger.info("--- Phase Two: Fine-tuning the optimal solution set using low-quality modules ---")
        if progress_callback: progress_callback("Phase Two: Fine-tuning top results...")
        unique_solutions = list({sol.get_combination_id(): sol for sol in all_best_solutions}.values())
        unique_solutions.sort(key=lambda s: s.optimization_score, reverse=True)
        
        refined_solutions = []
        if not low_quality_modules:
            self.logger.info("Low-quality module pool is empty, skipping fine-tuning phase.")
            refined_solutions = unique_solutions
        else:
            solutions_to_refine = unique_solutions[:30]
            for solution in solutions_to_refine:
                best_refined_solution = self._local_search_improvement(solution, candidate_modules, category, prioritized_attrs)
                if best_refined_solution.optimization_score > solution.optimization_score:
                     self.logger.info(f"Solution improved by fine-tuning! Score: {solution.optimization_score:.2f} -> {best_refined_solution.optimization_score:.2f}")
                refined_solutions.append(best_refined_solution)
        
        final_results = unique_solutions + refined_solutions
        for solution in final_results:
            if not solution.attr_breakdown:
                solution.score, solution.attr_breakdown = self.calculate_combat_power(solution.modules)

        # default sort by optimization score for stability before deduplication
        final_results.sort(key=lambda s: s.optimization_score, reverse=True)

        # Deduplicate by attribute-level signature
        solutions_by_attr_level = {}
        for solution in final_results:
            attr_level_key = self._get_attribute_level_key(solution.attr_breakdown)
            if attr_level_key not in solutions_by_attr_level:
                solutions_by_attr_level[attr_level_key] = solution

        deduplicated_solutions = list(solutions_by_attr_level.values())

        # If user requested priority-order mode and provided prioritized attributes, apply that ordering
        if prioritized_attrs and priority_order_mode:
            # compute priority sort key for each solution and sort by it descending
            deduplicated_solutions.sort(key=lambda s: self._compute_priority_sort_key(s, prioritized_attrs), reverse=True)
        else:
            # fallback: sort by final combat power score
            deduplicated_solutions.sort(key=lambda s: s.score, reverse=True)

        self.logger.info(f"Parallel optimization completed. Found {len(deduplicated_solutions)} high-quality combinations deduplicated by attribute level.")
        if progress_callback: progress_callback(f"Completed! Found {len(deduplicated_solutions)} unique combinations.")

        return deduplicated_solutions[:top_n]
    
    def _local_search_improvement(self, solution: ModuleSolution, module_pool: List[ModuleInfo], category: ModuleCategory, prioritized_attrs: Optional[List[str]]) -> ModuleSolution:
        fitness_cache: Dict[Tuple[int, ...], float] = {} if ENABLE_FITNESS_CACHE else {}
        best_solution = deepcopy(solution)
        best_solution.optimization_score = calculate_fitness(best_solution.modules, category, prioritized_attrs,
                                                           cache=fitness_cache if ENABLE_FITNESS_CACHE else None)
        while True:
            improved = False
            for i in range(len(best_solution.modules)):
                for new_module in module_pool:
                    if new_module.uuid in {m.uuid for m in best_solution.modules}: continue
                    temp_modules = best_solution.modules[:i] + [new_module] + best_solution.modules[i+1:]
                    new_score = calculate_fitness(temp_modules, category, prioritized_attrs,
                                                  cache=fitness_cache if ENABLE_FITNESS_CACHE else None)
                    if new_score > best_solution.optimization_score:
                        best_solution.modules = temp_modules
                        best_solution.optimization_score = new_score
                        best_solution.modules.sort(key=lambda m: m.uuid)
                        improved = True
                        break 
                if improved: break
            if not improved: break
        return best_solution
        
    def print_solution_details(self, solution: ModuleSolution, rank: int):
        header = f"\n=== Rank {rank} Combination (Fitness Score: {solution.optimization_score:.2f}) ==="
        print(header); self._log_result(header)
        total_value_str = f"Total Attribute Value: {sum(solution.attr_breakdown.values())}"
        print(total_value_str); self._log_result(total_value_str)
        combat_power_str = f"Combat Power: {solution.score}"
        print(combat_power_str); self._log_result(combat_power_str)
        print("\nModule List:"); self._log_result("\nModule List:")
        for i, module in enumerate(solution.modules, 1):
            parts_str = ", ".join([f"{p.name}+{p.value}" for p in module.parts])
            module_line = f"  {i}. {module.name} (Quality {module.quality}) - {parts_str}"
            print(module_line); self._log_result(module_line)
        print("\nAttribute Distribution:"); self._log_result("\nAttribute Distribution:")
        for attr_name, value in sorted(solution.attr_breakdown.items()):
            orname="(Level 0)"
            if value >= 20: orname = "(Level 6)"
            elif value >= 16: orname = "(Level 5)"
            elif value >= 12: orname = "(Level 4)"
            elif value >= 8: orname = "(Level 3)"
            elif value >= 4: orname = "(Level 2)"
            elif value >= 1: orname = "(Level 1)"
            attr_line = f"  {attr_name}{orname}: +{value}"
            print(attr_line); self._log_result(attr_line)

    def get_optimal_solutions(self, modules: List[ModuleInfo], category: ModuleCategory = ModuleCategory.All,
                           top_n: int = 40, prioritized_attrs: Optional[List[str]] = None,
                           priority_order_mode: bool = False,
                           progress_callback: Optional[Callable[[str], None]] = None) -> List[ModuleSolution]:
        """
        Optimizes modules and returns a list of solutions instead of printing them.
        """
        separator = f"\n{'='*50}"
        print(separator); self._log_result(separator)
        title = f"Module Combination Optimization - {category.value} Type"
        print(title); self._log_result(title)
        print(separator); self._log_result(separator)
        
        optimal_solutions = self.optimize_modules(modules, category, top_n, prioritized_attrs, priority_order_mode, progress_callback)

        if not optimal_solutions:
            msg = f"No valid combinations found that meet all filtering criteria.\nHint: Please check if the filtering attributes are too strict, or if the module pool lacks modules that meet the requirements."
            print(msg); self._log_result(msg)
            return []
        
        found_msg = f"\nFound {len(optimal_solutions)} optimal combinations deduplicated by attribute level."
        print(found_msg); self._log_result(found_msg)
        
        print(separator); self._log_result(separator)
        return optimal_solutions
