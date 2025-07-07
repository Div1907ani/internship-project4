#!/usr/bin/env python3
"""
Business Optimization: Production Planning Problem
==================================================

This script demonstrates how to solve a real-world business problem using
Linear Programming optimization techniques with the PuLP library.

Problem: A manufacturing company needs to optimize its production planning
to maximize profit while meeting demand constraints and resource limitations.

Author: AI Assistant
Date: 2024
"""

import pulp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ProductionPlanningOptimizer:
    """
    A class to solve production planning optimization problems using Linear Programming.
    
    This optimizer helps manufacturing companies determine the optimal production
    quantities for different products to maximize profit while respecting
    resource constraints and demand requirements.
    """
    
    def __init__(self):
        """Initialize the optimizer with default problem data."""
        self.problem = None
        self.results = None
        
        # Product information
        self.products = {
            'Product_A': {
                'profit_per_unit': 50,  # $50 profit per unit
                'labor_hours': 2,       # 2 hours of labor per unit
                'machine_hours': 1.5,   # 1.5 hours of machine time per unit
                'raw_material': 3,      # 3 kg of raw material per unit
                'max_demand': 100       # Maximum demand constraint
            },
            'Product_B': {
                'profit_per_unit': 75,
                'labor_hours': 3,
                'machine_hours': 2,
                'raw_material': 4,
                'max_demand': 80
            },
            'Product_C': {
                'profit_per_unit': 60,
                'labor_hours': 2.5,
                'machine_hours': 1.8,
                'raw_material': 3.5,
                'max_demand': 120
            }
        }
        
        # Resource constraints
        self.resources = {
            'labor_hours': 400,      # Total available labor hours
            'machine_hours': 300,    # Total available machine hours
            'raw_material': 1000     # Total available raw material (kg)
        }
        
        # Minimum production requirements (contractual obligations)
        self.min_production = {
            'Product_A': 20,
            'Product_B': 15,
            'Product_C': 25
        }
    
    def create_optimization_model(self) -> pulp.LpProblem:
        """
        Create and set up the linear programming model.
        
        Returns:
            pulp.LpProblem: The configured optimization problem
        """
        print("🔧 Creating optimization model...")
        
        # Create the optimization problem
        problem = pulp.LpProblem("Production_Planning_Optimization", pulp.LpMaximize)
        
        # Decision variables: quantity to produce for each product
        production_vars = pulp.LpVariable.dicts("Production",
                                               self.products.keys(),
                                               lowBound=0,
                                               cat='Integer')
        self.production_vars = production_vars  # Store as instance variable
        
        # Objective function: Maximize total profit
        objective = pulp.lpSum([self.products[product]['profit_per_unit'] * production_vars[product]
                               for product in self.products.keys()])
        problem += objective, "Total_Profit"
        
        # Constraints
        
        # 1. Labor hours constraint
        labor_constraint = pulp.lpSum([self.products[product]['labor_hours'] * production_vars[product]
                                      for product in self.products.keys()]) <= self.resources['labor_hours']
        problem += labor_constraint, "Labor_Hours_Limit"
        
        # 2. Machine hours constraint
        machine_constraint = pulp.lpSum([self.products[product]['machine_hours'] * production_vars[product]
                                        for product in self.products.keys()]) <= self.resources['machine_hours']
        problem += machine_constraint, "Machine_Hours_Limit"
        
        # 3. Raw material constraint
        material_constraint = pulp.lpSum([self.products[product]['raw_material'] * production_vars[product]
                                         for product in self.products.keys()]) <= self.resources['raw_material']
        problem += material_constraint, "Raw_Material_Limit"
        
        # 4. Maximum demand constraints
        for product in self.products.keys():
            demand_constraint = production_vars[product] <= self.products[product]['max_demand']
            problem += demand_constraint, f"Max_Demand_{product}"
        
        # 5. Minimum production constraints
        for product in self.products.keys():
            min_production_constraint = production_vars[product] >= self.min_production[product]
            problem += min_production_constraint, f"Min_Production_{product}"
        
        self.problem = problem
        print("✅ Optimization model created successfully!")
        return problem
    
    def solve_optimization(self) -> Dict:
        """
        Solve the optimization problem and return results.
        
        Returns:
            Dict: Dictionary containing optimization results
        """
        if self.problem is None:
            self.create_optimization_model()
        assert self.problem is not None  # Ensure problem is set
        print("🚀 Solving optimization problem...")
        status = self.problem.solve()
        
        # Check if solution was found
        if status == pulp.LpStatusOptimal:
            print("✅ Optimal solution found!")
            
            # Extract results
            results = {
                'status': 'Optimal',
                'total_profit': pulp.value(self.problem.objective),
                'production_quantities': {},
                'resource_usage': {},
                'constraint_analysis': {}
            }
            
            # Get production quantities
            for product in self.products.keys():
                results['production_quantities'][product] = int(pulp.value(self.production_vars[product]))
            
            # Calculate resource usage
            for resource in self.resources.keys():
                usage = sum(results['production_quantities'][product] * self.products[product][resource]
                           for product in self.products.keys())
                results['resource_usage'][resource] = {
                    'used': usage,
                    'available': self.resources[resource],
                    'utilization': (usage / self.resources[resource]) * 100
                }
            
            # Analyze constraints
            for constraint in self.problem.constraints:
                constraint_value = self.problem.constraints[constraint].value()
                results['constraint_analysis'][constraint] = constraint_value
            
            self.results = results
            return results
            
        else:
            print(f"❌ No optimal solution found. Status: {pulp.LpStatus[status]}")
            return {'status': 'Infeasible', 'message': f'Problem status: {pulp.LpStatus[status]}'}
    
    def display_results(self):
        """Display the optimization results in a formatted way."""
        if self.results is None:
            print("No results to display. Run solve_optimization() first.")
            return
        
        print("\n" + "="*60)
        print("📊 OPTIMIZATION RESULTS")
        print("="*60)
        
        # Overall results
        print(f"\n🎯 Total Profit: ${self.results['total_profit']:,.2f}")
        print(f"📈 Solution Status: {self.results['status']}")
        
        # Production quantities
        print(f"\n📦 PRODUCTION QUANTITIES:")
        print("-" * 40)
        for product, quantity in self.results['production_quantities'].items():
            profit = quantity * self.products[product]['profit_per_unit']
            print(f"{product:12}: {quantity:3d} units (${profit:,.2f} profit)")
        
        # Resource utilization
        print(f"\n⚙️  RESOURCE UTILIZATION:")
        print("-" * 40)
        for resource, data in self.results['resource_usage'].items():
            print(f"{resource:15}: {data['used']:6.1f} / {data['available']:6.1f} "
                  f"({data['utilization']:5.1f}%)")
        
        # Constraint analysis
        print(f"\n🔍 CONSTRAINT ANALYSIS:")
        print("-" * 40)
        for constraint, value in self.results['constraint_analysis'].items():
            print(f"{constraint:25}: {value:8.2f}")
    
    def create_visualizations(self):
        """Create comprehensive visualizations of the results."""
        if self.results is None:
            print("No results to visualize. Run solve_optimization() first.")
            return
        
        # Set up the plotting area
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Production Planning Optimization Results', fontsize=16, fontweight='bold')
        
        # 1. Production quantities bar chart
        products = list(self.results['production_quantities'].keys())
        quantities = list(self.results['production_quantities'].values())
        
        bars1 = axes[0, 0].bar(products, quantities, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        axes[0, 0].set_title('Optimal Production Quantities', fontweight='bold')
        axes[0, 0].set_ylabel('Units')
        axes[0, 0].set_ylim(0, max(quantities) * 1.1)
        
        # Add value labels on bars
        for bar, quantity in zip(bars1, quantities):
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{quantity}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Resource utilization pie chart
        resources = list(self.results['resource_usage'].keys())
        utilizations = [data['utilization'] for data in self.results['resource_usage'].values()]
        colors = ['#FF9999', '#66B2FF', '#99FF99']
        
        wedges, texts, autotexts = axes[0, 1].pie(utilizations, labels=resources, autopct='%1.1f%%',
                                                  colors=colors, startangle=90)
        axes[0, 1].set_title('Resource Utilization', fontweight='bold')
        
        # 3. Profit breakdown
        profits = [self.results['production_quantities'][product] * self.products[product]['profit_per_unit']
                  for product in products]
        
        bars2 = axes[1, 0].bar(products, profits, color=['#FFB366', '#FF99CC', '#99CCFF'])
        axes[1, 0].set_title('Profit Contribution by Product', fontweight='bold')
        axes[1, 0].set_ylabel('Profit ($)')
        
        # Add value labels on bars
        for bar, profit in zip(bars2, profits):
            height = bar.get_height()
            axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 100,
                           f'${profit:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Resource usage comparison
        resource_names = list(self.results['resource_usage'].keys())
        used = [data['used'] for data in self.results['resource_usage'].values()]
        available = [data['available'] for data in self.results['resource_usage'].values()]
        
        x = np.arange(len(resource_names))
        width = 0.35
        
        bars3 = axes[1, 1].bar(x - width/2, used, width, label='Used', color='#FF6B6B')
        bars4 = axes[1, 1].bar(x + width/2, available, width, label='Available', color='#4ECDC4')
        
        axes[1, 1].set_title('Resource Usage vs Availability', fontweight='bold')
        axes[1, 1].set_ylabel('Hours/Kg')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(resource_names)
        axes[1, 1].legend()
        
        # Add value labels
        for bar in bars3:
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + 5,
                           f'{height:.0f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.show()
    
    def sensitivity_analysis(self):
        """
        Perform sensitivity analysis to understand how changes in parameters
        affect the optimal solution.
        """
        print("\n" + "="*60)
        print("🔬 SENSITIVITY ANALYSIS")
        print("="*60)
        
        # Test different profit scenarios
        profit_scenarios = {
            'Base Case': self.products,
            'High Profit A': self._modify_profit('Product_A', 1.5),
            'High Profit B': self._modify_profit('Product_B', 1.5),
            'High Profit C': self._modify_profit('Product_C', 1.5)
        }
        
        sensitivity_results = {}
        
        for scenario_name, scenario_products in profit_scenarios.items():
            print(f"\n📊 Testing scenario: {scenario_name}")
            
            # Temporarily modify products
            original_products = self.products.copy()
            self.products = scenario_products
            
            # Solve with new parameters
            results = self.solve_optimization()
            if results['status'] == 'Optimal':
                sensitivity_results[scenario_name] = {
                    'total_profit': results['total_profit'],
                    'production': results['production_quantities']
                }
            
            # Restore original products
            self.products = original_products
        
        # Display sensitivity results
        print(f"\n📈 SENSITIVITY ANALYSIS RESULTS:")
        print("-" * 50)
        for scenario, data in sensitivity_results.items():
            print(f"{scenario:15}: ${data['total_profit']:,.2f}")
        
        return sensitivity_results
    
    def _modify_profit(self, product: str, multiplier: float) -> Dict:
        """Helper method to modify profit for sensitivity analysis."""
        modified_products = self.products.copy()
        modified_products[product]['profit_per_unit'] *= multiplier
        return modified_products
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive business report based on the optimization results.
        
        Returns:
            str: Formatted business report
        """
        if self.results is None:
            return "No results available for report generation."
        
        report = f"""
BUSINESS OPTIMIZATION REPORT
============================

Executive Summary:
------------------
The production planning optimization has identified an optimal solution that maximizes
profit while respecting all operational constraints. The recommended production plan
will generate a total profit of ${self.results['total_profit']:,.2f}.

Production Recommendations:
--------------------------
"""
        
        for product, quantity in self.results['production_quantities'].items():
            profit = quantity * self.products[product]['profit_per_unit']
            report += f"• {product}: {quantity} units (${profit:,.2f} contribution)\n"
        
        report += f"""
Resource Utilization:
---------------------
"""
        
        for resource, data in self.results['resource_usage'].items():
            report += f"• {resource}: {data['utilization']:.1f}% utilized "
            report += f"({data['used']:.1f}/{data['available']:.1f})\n"
        
        report += f"""
Key Insights:
-------------
1. The optimal solution utilizes {max(data['utilization'] for data in self.results['resource_usage'].values()):.1f}% of the most constrained resource.
2. Total production capacity is efficiently allocated across all products.
3. All minimum production requirements are met while maximizing profitability.

Implementation Recommendations:
------------------------------
1. Implement the recommended production quantities immediately.
2. Monitor resource utilization to ensure optimal performance.
3. Consider capacity expansion for the most constrained resource.
4. Regularly review and update the optimization model with new data.
"""
        
        return report


def main():
    """
    Main function to demonstrate the production planning optimization.
    """
    print("🏭 PRODUCTION PLANNING OPTIMIZATION")
    print("=" * 50)
    print("Solving a real-world business problem using Linear Programming")
    print("with the PuLP optimization library.\n")
    
    # Create optimizer instance
    optimizer = ProductionPlanningOptimizer()
    
    # Display problem setup
    print("📋 PROBLEM SETUP:")
    print("-" * 30)
    print("Products and their characteristics:")
    for product, data in optimizer.products.items():
        print(f"  {product}:")
        print(f"    - Profit per unit: ${data['profit_per_unit']}")
        print(f"    - Labor hours: {data['labor_hours']}")
        print(f"    - Machine hours: {data['machine_hours']}")
        print(f"    - Raw material: {data['raw_material']} kg")
        print(f"    - Max demand: {data['max_demand']} units")
        print(f"    - Min production: {optimizer.min_production[product]} units")
        print()
    
    print("Resource constraints:")
    for resource, amount in optimizer.resources.items():
        print(f"  {resource}: {amount}")
    print()
    
    # Solve the optimization problem
    results = optimizer.solve_optimization()
    
    # Display results
    optimizer.display_results()
    
    # Create visualizations
    print("\n📊 Generating visualizations...")
    optimizer.create_visualizations()
    
    # Perform sensitivity analysis
    print("\n🔬 Performing sensitivity analysis...")
    sensitivity_results = optimizer.sensitivity_analysis()
    
    # Generate business report
    print("\n📄 Generating business report...")
    report = optimizer.generate_report()
    print(report)
    
    # Save results to file
    print("\n💾 Saving results to file...")
    with open('optimization_results.txt', 'w') as f:
        f.write(report)
    
    print("\n✅ Optimization analysis completed successfully!")
    print("📁 Results saved to 'optimization_results.txt'")


if __name__ == "__main__":
    main() 