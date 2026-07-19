from src.dto.daily_price_dto import DailyPriceDTO
from src.models.daily_price import DailyPrice


class DailyPriceMapper:
    """
    Converts provider DTOs into domain models.
    """

    @staticmethod
    def to_domain(
        dto: DailyPriceDTO,
        company_id: int,
    ) -> DailyPrice:

        return DailyPrice(
            company_id=company_id,
            price_date=dto.price_date,
            open_price=dto.open_price,
            high_price=dto.high_price,
            low_price=dto.low_price,
            close_price=dto.close_price,
            adjusted_close=dto.adjusted_close,
            volume=dto.volume,
        )
        
    @staticmethod
    def to_domain_list(
        provider_prices,
        company_id,
        ):
        return [
            DailyPriceMapper.to_domain(
                dto,
                company_id,
            )
            for dto in provider_prices
        ]