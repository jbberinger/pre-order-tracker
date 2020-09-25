class Availability:
    """
    Represents the availability of a product
    """

    def __init__(
        self, available, company, availability_description, product_title, url
    ):
        self.available = available
        self.company = company
        self.product_title = product_title
        self.availability_description = availability_description
        self.url = url
