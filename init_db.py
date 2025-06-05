from src.app import create_app, init_database
from src.models import db

def main():
	print(" Init-ng Banking System DB...")
	app = create_app()

	with app.app_context():
		try:
			from src.models import User
			User.query.count()
			print("DB struct looks good") # no need to reset it
		except Exception as e:
			print(f"!!!!!!!!!!! DB STRUCT ISSUE DETECTED: {e}")
			print("+++ RESETTING DB... +++")
			db.drop_all() # to recreate
			print("dropped old tables")

		init_database()

		print("\n ========= DB INIT IS DONE ========= ")
		print("NOW data migration is possible -- python migrate_data.py")

if __name__ == '__main__':
	main()