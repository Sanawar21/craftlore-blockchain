from .create_account import AccountCreationHandler
from .create_asset import AssetCreationHandler
from .create_products import ProductsCreationHandler
from .bootstrap import BootstrapHandler
from .create_admin import AdminCreationHandler


listeners = [
    AccountCreationHandler,
    AssetCreationHandler,
    AdminCreationHandler,
    ProductsCreationHandler,
    BootstrapHandler
]