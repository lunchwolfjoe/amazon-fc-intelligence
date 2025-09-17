#!/usr/bin/env python3
'''
Redshift Connection Helper for MCP
This script provides connection strings for Redshift clusters
'''

def get_redshift_connection_info():
    '''Get Redshift connection information'''
    
    clusters = {
        'beta': {
            'host': 'beta-wwopscomp.c0g2hsdsbjbt.us-east-1.redshift.amazonaws.com',
            'port': 5439,
            'database': 'betawwopscomp',
            'account': '809700197057',
            'description': 'Beta compensation cluster'
        },
        'prod': {
            'host': 'wwopscomp.c3kniaapvgmz.us-east-1.redshift.amazonaws.com', 
            'port': 5439,
            'database': 'wwopscomp',
            'account': '183703362924',
            'description': 'Production compensation cluster'
        }
    }
    
    return clusters

def format_connection_string(cluster_info):
    '''Format PostgreSQL connection string for Redshift'''
    
    # Standard PostgreSQL connection string format
    conn_str = f"postgresql://username@{cluster_info['host']}:{cluster_info['port']}/{cluster_info['database']}"
    
    return conn_str

if __name__ == "__main__":
    clusters = get_redshift_connection_info()
    
    print("🎯 Redshift Cluster Information:")
    print("=" * 50)
    
    for name, info in clusters.items():
        print(f"\n{name.upper()} Cluster:")
        print(f"  Host: {info['host']}")
        print(f"  Port: {info['port']}")
        print(f"  Database: {info['database']}")
        print(f"  Account: {info['account']}")
        print(f"  Connection: {format_connection_string(info)}")
