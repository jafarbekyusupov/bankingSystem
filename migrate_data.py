import json
import os
from datetime import datetime
from src.app import create_app
from src.models import db, User, Account, Transaction, Loan

def load_json_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f: return json.load(f)
    return []

def migrate_users():
    usrData = load_json_data('data/users.json')
    migrCnt = 0
    skipCnt = 0

    for udata in usrData:
        xstUsr = User.query.filter((User.user_id == udata['user_id']) | (User.username == udata['username'])).first()
        if xstUsr: print(f" ==== SKIPPI USER -- '{udata['username']}' | alr exists ==== "); skipCnt += 1; continue

        try:
            user = User(
                username=udata['username'],
                password=udata['password'],
                email=udata['email'],
                full_name=udata['full_name'],
                role=udata.get('role', 'user'))
            user.user_id = udata['user_id']
            user.created_at = datetime.fromisoformat(udata['created_at'])

            db.session.add(user)
            migrCnt += 1
            print(f" ==== MIGRATED USER -- {udata['username']} ==== ")

        except Exception as e: print(f" === EROR MIGRATING USER -- {udata['username']}: {e} === "); continue

    if migrCnt>0: db.session.commit()
    print(f" ===== USERS: {migrCnt} migrated | {skipCnt} skipped")

def migrate_accounts():
    accsData = load_json_data('data/accounts.json')
    migrCnt = 0
    skipCnt = 0

    for accdata in accsData:
        xstAcc = Account.query.filter_by(account_id=accdata['account_id']).first()
        if xstAcc: print(f" === SKIPPING ACC -- '{accdata['account_number']}' | alr exists === "); skipCnt += 1; continue

        usrXst = User.query.filter_by(user_id=accdata['user_id']).first()
        if not usrXst: print(f" === SKIPPING ACC -- '{accdata['account_number']}' | user not found === "); skipCnt += 1; continue

        try:
            acc = Account(user_id=accdata['user_id'],account_type=accdata['account_type'],balance=accdata['balance'],account_number=accdata['account_number'])
            acc.account_id = accdata['account_id']
            acc.created_at = datetime.fromisoformat(accdata['created_at'])
            acc.active = accdata.get('active', True)

            db.session.add(acc)
            migrCnt += 1
            print(f" ==== MIGRATED ACCS -- {accdata['account_number']} ==== ")

        except Exception as e:
            print(f" === EROR MIGRAING ACC {accdata['account_number']}: {e} === ")
            continue

    if migrCnt>0: db.session.commit()
    print(f" ===== ACCS: {migrCnt} migrated | {skipCnt} skipped ===== ")

def migrate_transactions():
    transacData = load_json_data('data/transactions.json')
    migrCnt = 0
    skipCnt = 0

    for trdata in transacData:
        xstTrsc = Transaction.query.filter_by(transaction_id=trdata['transaction_id']).first()
        if xstTrsc: skipCnt += 1; continue

        accXsts = Account.query.filter_by(account_id=trdata['account_id']).first()
        if not accXsts: print(f" !!!!!! SKIPPIN TRANSAC CUZ ACC NOT FOUND !!!!!!"); skipCnt += 1; continue

        try:
            transac = Transaction(
                account_id=trdata['account_id'],
                transaction_type=trdata['transaction_type'],
                amount=trdata['amount'],
                description=trdata.get('description'),
                destination_account_id=trdata.get('destination_account_id'))
            transac.transaction_id = trdata['transaction_id']
            transac.created_at = datetime.fromisoformat(trdata['created_at'])
            db.session.add(transac)
            migrCnt += 1

        except Exception as e: print(f" !!!!!! Error migrating transaction -- {e}"); continue

    if migrCnt>0: db.session.commit()
    print(f" ===== TRANSACTOINS: {migrCnt} migrated | {skipCnt} skipped")

def migrate_loans():
    loansData = load_json_data('data/loans.json')
    migrCnt = 0
    skipCnt = 0

    for ldata in loansData:
        xstLoan = Loan.query.filter_by(loan_id=ldata['loan_id']).first()
        if xstLoan: skipCnt += 1; continue

        usrXst = User.query.filter_by(user_id=ldata['user_id']).first()
        if not usrXst: print(f" === SKIPPING LOAN | user not found === "); skipCnt += 1; continue

        try:
            loan = Loan(
                user_id=ldata['user_id'],
                loan_type=ldata['loan_type'],
                amount=ldata['amount'],
                interest_rate=ldata['interest_rate'],
                term_months=ldata['term_months'],
                purpose=ldata.get('purpose'),
                status=ldata.get('status', 'pending'),
                balance=ldata.get('balance', ldata['amount']))
            loan.loan_id = ldata['loan_id']
            loan.created_at = datetime.fromisoformat(ldata['created_at'])
            if ldata.get('approved_at'): loan.approved_at = datetime.fromisoformat(ldata['approved_at'])

            db.session.add(loan)
            migrCnt += 1
            print(f" ==== MIGRATED LOAN -- {ldata['loan_type']} - ${ldata['amount']} ==== ")

        except Exception as e: print(f" === ERROR MIGRATNG LOAN {e} === "); continue

    if migrCnt>0: db.session.commit()
    print(f" ==== LOANS -- {migrCnt} migrated | {skipCnt} skipped")

def show_database_summary(): # show curr DB state
    try:
        usrCnt = User.query.count()
        acCnt = Account.query.count()
        trCnt = Transaction.query.count()
        lcnt = Loan.query.count()

        print(f"\n ==== DB SYMMARY ====")
        print(f" -- Users - {usrCnt}")
        print(f" -- Accounts - {acCnt}")
        print(f" -- Transactions - {trCnt}")
        print(f" -- Loans - {lcnt}")

        if usrCnt>0:
            print(f"\n === SAMPLE USERS === ")
            users = User.query.limit(3).all()
            for i in users: print(f" -- {i.username} ({i.role})")

    except Exception as e: print(f" !!! EEROR DISPLAYING DB SUMMARY -- {e} !!!")

def main():
    print(" Starting data migration from JSON to DB...")

    json_files = ['data/users.json', 'data/accounts.json', 'data/transactions.json', 'data/loans.json']
    xstFls = [f for f in json_files if os.path.exists(f)]
    missFls = [f for f in json_files if not os.path.exists(f)]

    if missFls: print(f" !!! missing JSON files -- {missFls} !!! ")

    if not xstFls: print(" ##### no json files found ##### "); return

    print(f" ===== FOUND JSON FILES -- {xstFls} =====")
    app = create_app()
    with app.app_context():
        try:
            User.query.count()  # test query
            print(" ===== DB connection verified =====") # db prperly inited
        except Exception as e:
            print(f" !!! DB NOT PROPERLY INITTED -- {e}")
            print(" !!! FIX -- run: `python init_db.py`")
            return

        print("\n === migrating data... === ")

        migrate_users()
        migrate_accounts()
        migrate_transactions()
        migrate_loans()
        show_database_summary()

        print(" ++++++++++++++++++++++++++++++++++++++")
        print("\n ++++++ DATA MIGRATION COMPLETED +++++")
        print(" ++++++++++++++++++++++++++++++++++++++")

if __name__ == '__main__':
    main()