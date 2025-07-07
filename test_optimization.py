#!/usr/bin/env python3
"""
Simplified test of the production planning optimization
"""

import pulp
import warnings
warnings.filterwarnings('ignore')

def test_optimization():
    """Test the optimization without visualizations"""
    
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
    
    print("🏭 PRODUCTION PLANNING OPTIMIZATION TEST")
    print("=" * 50)
    
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
    
    print("🔧 Model created successfully!")
    
    # Solve
    status = prob.solve()
    print(f"🚀 Solution status: {pulp.LpStatus[prob.status]}")
    
    if status == pulp.LpStatusOptimal:
        print("✅ Optimal solution found!")
        
        # Extract results
        production_quantities = {p: int(production_vars[p].varValue) for p in products}
        total_profit = pulp.value(prob.objective)
        
        print(f"\n📊 RESULTS:")
        print(f"🎯 Total Profit: ${total_profit:,.2f}")
        print(f"\n📦 Production Quantities:")
        for p, q in production_quantities.items():
            profit = q * products[p]['profit_per_unit']
            print(f"  {p}: {q} units (${profit:,.2f} profit)")
        
        print(f"\n⚙️ Resource Utilization:")
        for resource in resources:
            used = sum(production_quantities[p] * products[p][resource] for p in products)
            available = resources[resource]
            utilization = used / available * 100
            print(f"  {resource}: {used:.1f} / {available} ({utilization:.1f}%)")
        
        print(f"\n✅ Optimization completed successfully!")
        return True
    else:
        print(f"❌ No optimal solution found. Status: {pulp.LpStatus[status]}")
        return False

if __name__ == "__main__":
    test_optimization() 