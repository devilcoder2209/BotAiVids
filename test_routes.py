from app import app

def list_management_routes():
    with app.app_context():
        print("User Management Routes:")
        for rule in app.url_map.iter_rules():
            if 'manage' in rule.endpoint:
                print(f"  {rule.rule} -> {rule.endpoint}")

if __name__ == "__main__":
    list_management_routes()
