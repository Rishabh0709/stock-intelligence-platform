from src.bootstrap import Bootstrap


class CLI:

    def __init__(self):
        
        self.app = Bootstrap()


    def import_company(self, symbol):

        company = self.service.import_company(symbol)

        print(company)

    def list_companies(self):

        companies = self.service.get_all_companies()

        for company in companies:
            print(company.symbol, "-", company.company_name)

    def search_company(self, symbol):

        company = self.service.get_company(symbol)

        print(company)
        
    def sync(self, symbol: str):

        company = self.app.company_repository.get_by_symbol(symbol)

        if company is None:
            print(f"Company '{symbol}' not found.")
            return

        result = self.app.price_sync_service.sync(company)

        print()
        print("=" * 40)
        print(f"Company     : {result.company_symbol}")
        print(f"Downloaded  : {result.downloaded_records}")
        print(f"Inserted    : {result.inserted_records}")
        print(f"Updated     : {result.updated_records}")
        print(f"Skipped     : {result.skipped_records}")
        print(f"Latest Date : {result.latest_price_date}")
        print("=" * 40)
