import app.db
import app.model

def main():
    app.db.create_db_and_tables()
    print("started!!!")

if __name__ == "__main__":
    main()
