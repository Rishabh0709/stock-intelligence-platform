from src.bootstrap import Bootstrap
from src.models.portfolio_holding import PortfolioHolding

bootstrap = Bootstrap()

repo = bootstrap.portfolio_repository

repo.clear()

holding = PortfolioHolding(
    company_id=1,
    quantity=25,
    average_price=1450.75,
)

repo.add(holding)

print(repo.get_all())

print(repo.count())

repo.update(
    PortfolioHolding(
        company_id=1,
        quantity=30,
        average_price=1500,
    )
)

print(repo.get(1))

repo.delete(1)

print(repo.count())