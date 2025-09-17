#!/usr/bin/env python3
"""
Compensation Data Simulator
Creates realistic sample compensation data for AI framework testing
"""

import pandas as pd
import numpy as np
import sqlite3
import random
from datetime import datetime, timedelta
import json

def create_sample_compensation_database():
    """Create a SQLite database with realistic compensation data"""
    
    # Create in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    
    # Set random seed for reproducible data
    np.random.seed(42)
    random.seed(42)
    
    # Job levels and titles
    job_levels = {
        'L4': ['Software Engineer I', 'Data Analyst I', 'Product Manager I'],
        'L5': ['Software Engineer II', 'Data Analyst II', 'Product Manager II'], 
        'L6': ['Senior Software Engineer', 'Senior Data Analyst', 'Senior Product Manager'],
        'L7': ['Principal Engineer', 'Principal Data Scientist', 'Principal Product Manager'],
        'L8': ['Distinguished Engineer', 'Distinguished Scientist', 'Director']
    }
    
    # Locations with cost of living multipliers
    locations = {
        'Seattle, WA': 1.15,
        'San Francisco, CA': 1.35,
        'New York, NY': 1.25,
        'Austin, TX': 1.05,
        'Denver, CO': 1.08,
        'Boston, MA': 1.20,
        'Atlanta, GA': 1.00,
        'Portland, OR': 1.10
    }
    
    # Generate employee data
    employees = []
    employee_id = 1000
    
    for _ in range(1000):  # 1000 sample employees
        level = random.choice(list(job_levels.keys()))
        title = random.choice(job_levels[level])
        location = random.choice(list(locations.keys()))
        cost_multiplier = locations[location]
        
        # Base salary ranges by level
        base_ranges = {
            'L4': (95000, 120000),
            'L5': (120000, 150000),
            'L6': (150000, 200000),
            'L7': (200000, 280000),
            'L8': (280000, 400000)
        }
        
        base_min, base_max = base_ranges[level]
        base_salary = int(np.random.uniform(base_min, base_max) * cost_multiplier)
        
        # Stock and bonus calculations
        stock_value = int(base_salary * np.random.uniform(0.3, 0.8))
        bonus_target = int(base_salary * np.random.uniform(0.15, 0.25))
        
        # Demographics (anonymized)
        hire_date = datetime.now() - timedelta(days=random.randint(30, 2000))
        
        employees.append({
            'employee_id': employee_id,
            'job_level': level,
            'job_title': title,
            'location': location,
            'base_salary': base_salary,
            'stock_value': stock_value,
            'bonus_target': bonus_target,
            'hire_date': hire_date.strftime('%Y-%m-%d'),
            'department': random.choice(['Engineering', 'Product', 'Data Science', 'Operations']),
            'manager_id': random.randint(2000, 2100) if random.random() > 0.1 else None
        })
        employee_id += 1
    
    # Create employees table
    df_employees = pd.DataFrame(employees)
    df_employees.to_sql('employees', conn, index=False)
    
    # Generate market survey data
    market_data = []
    for level in job_levels.keys():
        for location in locations.keys():
            base_min, base_max = base_ranges[level]
            cost_multiplier = locations[location]
            
            market_data.append({
                'job_level': level,
                'location': location,
                'market_p50': int(np.random.uniform(base_min, base_max) * cost_multiplier),
                'market_p25': int(np.random.uniform(base_min * 0.9, base_min) * cost_multiplier),
                'market_p75': int(np.random.uniform(base_max, base_max * 1.1) * cost_multiplier),
                'survey_date': '2024-Q2',
                'source': 'Radford Survey'
            })
    
    df_market = pd.DataFrame(market_data)
    df_market.to_sql('market_survey', conn, index=False)
    
    # Generate compensation changes/history
    comp_changes = []
    change_id = 1
    
    for emp in employees[:200]:  # Sample of employees with changes
        if random.random() > 0.3:  # 70% have had changes
            num_changes = random.randint(1, 3)
            
            for i in range(num_changes):
                change_date = datetime.strptime(emp['hire_date'], '%Y-%m-%d') + timedelta(days=random.randint(180, 700))
                
                change_type = random.choice(['promotion', 'market_adjustment', 'merit_increase'])
                
                if change_type == 'promotion':
                    increase_pct = np.random.uniform(0.15, 0.25)
                elif change_type == 'market_adjustment':
                    increase_pct = np.random.uniform(0.05, 0.12)
                else:  # merit_increase
                    increase_pct = np.random.uniform(0.03, 0.08)
                
                old_salary = emp['base_salary']
                new_salary = int(old_salary * (1 + increase_pct))
                
                comp_changes.append({
                    'change_id': change_id,
                    'employee_id': emp['employee_id'],
                    'change_date': change_date.strftime('%Y-%m-%d'),
                    'change_type': change_type,
                    'old_salary': old_salary,
                    'new_salary': new_salary,
                    'increase_pct': round(increase_pct * 100, 2),
                    'reason': f"Annual {change_type.replace('_', ' ')}"
                })
                change_id += 1
    
    df_changes = pd.DataFrame(comp_changes)
    df_changes.to_sql('compensation_changes', conn, index=False)
    
    return conn

def run_sample_queries(conn):
    """Run sample compensation analysis queries"""
    
    queries = {
        'Employee Count by Level': """
            SELECT job_level, COUNT(*) as employee_count
            FROM employees 
            GROUP BY job_level 
            ORDER BY job_level;
        """,
        
        'Average Salary by Location': """
            SELECT location, 
                   AVG(base_salary) as avg_salary,
                   COUNT(*) as employee_count
            FROM employees 
            GROUP BY location 
            ORDER BY avg_salary DESC;
        """,
        
        'Pay Equity Analysis': """
            SELECT job_level,
                   location,
                   AVG(base_salary) as avg_salary,
                   MIN(base_salary) as min_salary,
                   MAX(base_salary) as max_salary,
                   COUNT(*) as count
            FROM employees
            GROUP BY job_level, location
            HAVING COUNT(*) >= 3
            ORDER BY job_level, location;
        """,
        
        'Market Competitiveness': """
            SELECT e.job_level,
                   e.location,
                   AVG(e.base_salary) as internal_avg,
                   m.market_p50,
                   ROUND((AVG(e.base_salary) - m.market_p50) * 100.0 / m.market_p50, 2) as variance_pct
            FROM employees e
            JOIN market_survey m ON e.job_level = m.job_level AND e.location = m.location
            GROUP BY e.job_level, e.location, m.market_p50
            ORDER BY variance_pct;
        """,
        
        'Recent Compensation Changes': """
            SELECT c.change_type,
                   COUNT(*) as change_count,
                   AVG(c.increase_pct) as avg_increase_pct,
                   AVG(c.new_salary - c.old_salary) as avg_increase_amount
            FROM compensation_changes c
            WHERE c.change_date >= '2024-01-01'
            GROUP BY c.change_type
            ORDER BY avg_increase_pct DESC;
        """
    }
    
    print("🔍 Sample Compensation Analysis Results:")
    print("=" * 60)
    
    for query_name, sql in queries.items():
        print(f"\n📊 {query_name}:")
        print("-" * 40)
        
        try:
            df = pd.read_sql_query(sql, conn)
            print(df.to_string(index=False))
        except Exception as e:
            print(f"❌ Error: {e}")

def create_ai_training_examples(conn):
    """Create examples of how AI would analyze this data"""
    
    print(f"\n🤖 AI Analysis Examples:")
    print("=" * 60)
    
    # Example 1: Pay Equity Analysis
    print(f"\n1️⃣ AI Pay Equity Analysis:")
    print("-" * 30)
    
    equity_sql = """
        SELECT job_level, location, 
               COUNT(*) as count,
               AVG(base_salary) as avg_salary,
               STDDEV(base_salary) as salary_stddev
        FROM employees 
        WHERE job_level = 'L6'
        GROUP BY job_level, location
        HAVING COUNT(*) >= 5;
    """
    
    df_equity = pd.read_sql_query(equity_sql, conn)
    print("Raw Data:")
    print(df_equity.to_string(index=False))
    
    print(f"\n🤖 AI Interpretation:")
    print("Based on this L6 data, I can see potential pay equity concerns:")
    
    if len(df_equity) > 1:
        max_avg = df_equity['avg_salary'].max()
        min_avg = df_equity['avg_salary'].min()
        variance = ((max_avg - min_avg) / min_avg) * 100
        
        print(f"• Salary variance across locations: {variance:.1f}%")
        if variance > 20:
            print("• ⚠️ High variance detected - review for cost-of-living adjustments")
        else:
            print("• ✅ Variance within acceptable range")
    
    # Example 2: Market Competitiveness
    print(f"\n2️⃣ AI Market Competitiveness Analysis:")
    print("-" * 40)
    
    market_sql = """
        SELECT e.job_level,
               AVG(e.base_salary) as internal_avg,
               AVG(m.market_p50) as market_avg,
               ROUND((AVG(e.base_salary) - AVG(m.market_p50)) * 100.0 / AVG(m.market_p50), 2) as competitiveness_pct
        FROM employees e
        JOIN market_survey m ON e.job_level = m.job_level AND e.location = m.location
        GROUP BY e.job_level
        ORDER BY e.job_level;
    """
    
    df_market = pd.read_sql_query(market_sql, conn)
    print("Market Analysis:")
    print(df_market.to_string(index=False))
    
    print(f"\n🤖 AI Recommendations:")
    for _, row in df_market.iterrows():
        level = row['job_level']
        comp_pct = row['competitiveness_pct']
        
        if comp_pct < -5:
            print(f"• {level}: Below market by {abs(comp_pct):.1f}% - consider market adjustment")
        elif comp_pct > 10:
            print(f"• {level}: Above market by {comp_pct:.1f}% - monitor for budget impact")
        else:
            print(f"• {level}: Competitive positioning ({comp_pct:+.1f}%)")

def main():
    """Main function to demonstrate AI compensation analysis"""
    
    print("🎯 Compensation AI Framework - Data Simulation")
    print("=" * 60)
    
    print("📊 Creating sample compensation database...")
    conn = create_sample_compensation_database()
    
    print("✅ Sample database created with:")
    print("   • 1,000 employees across 5 job levels")
    print("   • 8 geographic locations")
    print("   • Market survey data")
    print("   • Compensation change history")
    
    # Run sample queries
    run_sample_queries(conn)
    
    # Show AI analysis examples
    create_ai_training_examples(conn)
    
    print(f"\n🚀 Next Steps:")
    print("=" * 60)
    print("This simulation demonstrates how the AI framework would:")
    print("1. ✅ Query compensation data from Redshift")
    print("2. ✅ Perform statistical analysis and pattern detection")
    print("3. ✅ Generate insights and recommendations")
    print("4. ✅ Flag potential equity or compliance issues")
    print("5. ✅ Provide natural language explanations")
    
    print(f"\nOnce you have access to the real Redshift clusters,")
    print(f"I can run similar analyses on your actual compensation data!")
    
    conn.close()

if __name__ == "__main__":
    main()