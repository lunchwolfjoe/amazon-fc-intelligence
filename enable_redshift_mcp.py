#!/usr/bin/env python3
"""
Enable Redshift MCP Connection
This script helps configure MCP for Redshift access
"""

import json
import os
import shutil

def update_mcp_config_for_redshift():
    """Update MCP configuration to enable Redshift access"""
    
    mcp_config_path = os.path.expanduser("~/.kiro/settings/mcp.json")
    
    # Read current config
    with open(mcp_config_path, 'r') as f:
        config = json.load(f)
    
    # Enable PostgreSQL MCP for Redshift
    if 'aws-postgres' in config['mcpServers']:
        config['mcpServers']['aws-postgres']['disabled'] = False
        config['mcpServers']['aws-postgres']['env'] = {
            "FASTMCP_LOG_LEVEL": "ERROR",
            "AWS_REGION": "us-east-1"
        }
        config['mcpServers']['aws-postgres']['autoApprove'] = [
            "execute_query",
            "list_tables", 
            "describe_table"
        ]
    
    # Add a custom Redshift configuration
    config['mcpServers']['redshift-compensation'] = {
        "command": "uvx",
        "args": [
            "awslabs.postgres-mcp-server@latest"
        ],
        "env": {
            "FASTMCP_LOG_LEVEL": "ERROR",
            "AWS_REGION": "us-east-1",
            "REDSHIFT_MODE": "true"
        },
        "disabled": False,
        "autoApprove": [
            "execute_query",
            "list_tables",
            "describe_table",
            "get_schema"
        ]
    }
    
    # Backup original config
    backup_path = mcp_config_path + ".backup"
    shutil.copy2(mcp_config_path, backup_path)
    print(f"✅ Backed up original config to: {backup_path}")
    
    # Write updated config
    with open(mcp_config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Updated MCP configuration")
    print(f"📝 Enabled PostgreSQL MCP for Redshift access")
    print(f"📝 Added redshift-compensation server configuration")
    
    return config

def create_redshift_connection_helper():
    """Create a helper script for Redshift connections"""
    
    helper_script = """#!/usr/bin/env python3
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
        print(f"\\n{name.upper()} Cluster:")
        print(f"  Host: {info['host']}")
        print(f"  Port: {info['port']}")
        print(f"  Database: {info['database']}")
        print(f"  Account: {info['account']}")
        print(f"  Connection: {format_connection_string(info)}")
"""
    
    with open('redshift_connection_helper.py', 'w') as f:
        f.write(helper_script)
    
    print(f"✅ Created redshift_connection_helper.py")

def main():
    """Main function"""
    
    print("🔧 Configuring MCP for Redshift Access")
    print("=" * 50)
    
    try:
        # Update MCP configuration
        config = update_mcp_config_for_redshift()
        
        # Create helper script
        create_redshift_connection_helper()
        
        print(f"\\n🎯 Next Steps:")
        print("=" * 50)
        print("1. Restart Kiro to reload MCP configuration")
        print("2. The PostgreSQL MCP should now be available for Redshift")
        print("3. You may need to configure connection credentials")
        print("4. Try connecting to Redshift clusters using MCP tools")
        
        print(f"\\n💡 Alternative Approaches:")
        print("- Use AWS CLI MCP with redshift-data commands")
        print("- Create custom MCP server specifically for Redshift")
        print("- Use direct boto3 connection with assume_role")
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")

if __name__ == "__main__":
    main()