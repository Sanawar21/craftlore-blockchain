from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import AdminAccount
from models.enums import EventType, AdminPermissionLevel, AdminAccountStatus


class ValidateAdminAccount(BaseListener):
    def __init__(self):
        super().__init__([EventType.ADMIN_CREATED, EventType.CERTIFICATION_ISSUED, EventType.EDITED_BY_MODERATOR, EventType.ENTITY_AUTHENTICATED], priorities=[-1000, -1000, -1000, -1000])  # run after updating owner history
        self.valid_admins = {
            AdminPermissionLevel.SUPER_ADMIN: [EventType.ADMIN_CREATED],
            AdminPermissionLevel.CERTIFIER: [EventType.CERTIFICATION_ISSUED],
            AdminPermissionLevel.MODERATOR: [EventType.EDITED_BY_MODERATOR],
            AdminPermissionLevel.AUTHENTICATOR: [EventType.ENTITY_AUTHENTICATED],
        }

    def on_event(self, event: EventContext):
        admin: AdminAccount = event.get_data("admin")

        if not admin:
            raise InvalidTransaction("Account data not found in event context for ValidateAdminAccount")

        if admin.permission_level not in self.valid_admins:
            raise InvalidTransaction(f"Account type {admin.account_type} cannot perform any admin actions")

        if admin.is_deleted:
            raise InvalidTransaction("Deleted accounts cannot create assets")

        if admin.status != AdminAccountStatus.ACTIVE:
            raise InvalidTransaction("Only active admin accounts can perform admin actions")

        if event.event_type not in self.valid_admins[admin.permission_level]:
            raise InvalidTransaction(f"Account type {admin.account_type} cannot perform action {event.event_type}")
