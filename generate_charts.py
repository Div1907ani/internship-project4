#!/usr/bin/env python3
"""
Generate comprehensive visualizations for the production planning optimization results
"""

import pulp
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def solve_optimization():
    """Solve the optimization problem and return results"""
    
    # Product information
    products = {
        'Product_A': {
            'profit_per_unit': 50,
            'labor_hours': 2,
            'machine_hours': 1.5,
            'raw_material': 3,
            'max_demand': 100
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
    resources = {
        'labor_hours': 400,
        'machine_hours': 300,
        'raw_material': 1000
    }
    
    # Minimum production requirements
    min_production = {
        'Product_A': 20,
        'Product_B': 15,
        'Product_C': 25
    }
    
    # Create the optimization problem
    prob = pulp.LpProblem("Production_Planning_Optimization", pulp.LpMaximize)
    
    # Decision variables
    production_vars = pulp.LpVariable.dicts("Production", products.keys(), lowBound=0, cat='Integer')
    
    # Objective function: Maximize total profit
    prob += pulp.lpSum([products[p]['profit_per_unit'] * production_vars[p] for p in products]), "Total_Profit"
    
    # Constraints
    # Labor hours
    prob += pulp.lpSum([products[p]['labor_hours'] * production_vars[p] for p in products]) <= resources['labor_hours'], "Labor_Hours_Limit"
    # Machine hours
    prob += pulp.lpSum([products[p]['machine_hours'] * production_vars[p] for p in products]) <= resources['machine_hours'], "Machine_Hours_Limit"
    # Raw material
    prob += pulp.lpSum([products[p]['raw_material'] * production_vars[p] for p in products]) <= resources['raw_material'], "Raw_Material_Limit"
    # Maximum demand
    for p in products:
        prob += production_vars[p] <= products[p]['max_demand'], f"Max_Demand_{p}"
    # Minimum production
    for p in products:
        prob += production_vars[p] >= min_production[p], f"Min_Production_{p}"
    
    # Solve
    status = prob.solve()
    
    if status == pulp.LpStatusOptimal:
        # Extract results
        production_quantities = {p: int(production_vars[p].varValue) for p in products}
        total_profit = pulp.value(prob.objective)
        
        # Calculate resource usage
        resource_usage = {}
        for resource in resources:
            used = sum(production_quantities[p] * products[p][resource] for p in products)
            available = resources[resource]
            utilization = used / available * 100
            resource_usage[resource] = {
                'used': used,
                'available': available,
                'utilization': utilization
            }
        
        return {
            'production_quantities': production_quantities,
            'total_profit': total_profit,
            'resource_usage': resource_usage,
            'products': products
        }
    else:
        return None

def create_comprehensive_visualizations(results):
    """Create comprehensive visualizations of the optimization results"""
    
    if results is None:
        print("No results to visualize")
        return
    
    # Set up the plotting area with 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Production Planning Optimization Results', fontsize=18, fontweight='bold')
    
    # 1. Production quantities bar chart
    products = list(results['production_quantities'].keys())
    quantities = list(results['production_quantities'].values())
    
    bars1 = axes[0, 0].bar(products, quantities, color=['#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.8)
    axes[0, 0].set_title('Optimal Production Quantities', fontweight='bold', fontsize=14)
    axes[0, 0].set_ylabel('Units', fontweight='bold')
    axes[0, 0].set_ylim(0, max(quantities) * 1.1)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, quantity in zip(bars1, quantities):
        height = bar.get_height()
        axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + 2,
                       f'{quantity}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # 2. Resource utilization pie chart
    resources = list(results['resource_usage'].keys())
    utilizations = [results['resource_usage'][r]['utilization'] for r in resources]
    colors = ['#FF9999', '#66B2FF', '#99FF99']
    
    wedges, texts, autotexts = axes[0, 1].pie(utilizations, labels=resources, autopct='%1.1f%%',
                                              colors=colors, startangle=90, explode=(0.05, 0.05, 0.05))
    axes[0, 1].set_title('Resource Utilization', fontweight='bold', fontsize=14)
    
    # 3. Profit breakdown
    profits = [results['production_quantities'][product] * results['products'][product]['profit_per_unit']
              for product in products]
    
    bars2 = axes[1, 0].bar(products, profits, color=['#FFB366', '#FF99CC', '#99CCFF'], alpha=0.8)
    axes[1, 0].set_title('Profit Contribution by Product', fontweight='bold', fontsize=14)
    axes[1, 0].set_ylabel('Profit ($)', fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, profit in zip(bars2, profits):
        height = bar.get_height()
        axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 100,
                       f'${profit:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # 4. Resource usage comparison
    resource_names = list(results['resource_usage'].keys())
    used = [results['resource_usage'][r]['used'] for r in resource_names]
    available = [results['resource_usage'][r]['available'] for r in resource_names]
    
    x = np.arange(len(resource_names))
    width = 0.35
    
    bars3 = axes[1, 1].bar(x - width/2, used, width, label='Used', color='#FF6B6B', alpha=0.8)
    bars4 = axes[1, 1].bar(x + width/2, available, width, label='Available', color='#4ECDC4', alpha=0.8)
    
    axes[1, 1].set_title('Resource Usage vs Availability', fontweight='bold', fontsize=14)
    axes[1, 1].set_ylabel('Hours/Kg', fontweight='bold')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(resource_names)
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars3:
        height = bar.get_height()
        axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + 5,
                       f'{height:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    # Additional chart: Profit vs Resource Efficiency
    print(f"\n📊 Total Profit: ${results['total_profit']:,.2f}")
    print(f"📈 Most Constrained Resource: {max(results['resource_usage'].items(), key=lambda x: x[1]['utilization'])[0]}")

def main():
    """Main function to run optimization and generate charts"""
    print("📊 Generating Optimization Charts...")
    print("=" * 50)
    
    # Solve the optimization
    results = solve_optimization()
    
    if results:
        print("✅ Optimization solved successfully!")
        print(f"🎯 Total Profit: ${results['total_profit']:,.2f}")
        
        # Create visualizations
        print("\n📈 Creating comprehensive visualizations...")
        create_comprehensive_visualizations(results)
        
        print("\n✅ Charts generated successfully!")
    else:
        print("❌ Failed to solve optimization problem")

if __name__ == "__main__":
    main() 