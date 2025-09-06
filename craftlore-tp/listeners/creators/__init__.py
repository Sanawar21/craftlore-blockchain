from .create_account import AccountCreationHandler
from .create_asset import AssetCreationHandler
from .create_products import ProductsCreationHandler

listeners = [
    AccountCreationHandler,
    AssetCreationHandler,
    ProductsCreationHandler,
]