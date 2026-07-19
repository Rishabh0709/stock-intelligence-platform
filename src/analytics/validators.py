class AnalyticsValidator:
    """
    Shared validation helpers for analytics.
    """

    @staticmethod
    def positive(
        value,
        name: str = "Value",
    ) -> None:

        if value <= 0:

            raise ValueError(
                f"{name} must be positive."
            )

    @staticmethod
    def non_negative(
        value,
        name: str = "Value",
    ) -> None:

        if value < 0:

            raise ValueError(
                f"{name} cannot be negative."
            )

    @staticmethod
    def fast_less_than_slow(
        fast: int,
        slow: int,
    ) -> None:

        if fast >= slow:

            raise ValueError(
                "Fast period must be smaller than slow period."
            )

    @staticmethod
    def not_empty(
        values,
        name="Values",
    ) -> None:

        if not values:

            raise ValueError(
                f"{name} cannot be empty."
            )

    @staticmethod
    def enough_data(
        available: int,
        required: int,
    ) -> None:

        if available < required:

            raise ValueError(
                f"Need at least {required} observations."
            )