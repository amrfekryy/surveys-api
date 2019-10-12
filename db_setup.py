from models import *

def main():
    db.drop_all()
    db.create_all()
    print("\nDatabase setup completed successfully\n")

if __name__ == "__main__":
    with app.app_context():
        main()
