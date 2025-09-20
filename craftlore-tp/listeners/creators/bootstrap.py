from typing import Any


from .. import BaseListener, EventContext, InvalidTransaction
from models.enums import AccountType, EventType, AdminPermissionLevel, AuthenticationStatus
from models.classes.accounts import AdminAccount


class BootstrapHandler(BaseListener):
    def __init__(self):
        super().__init__([EventType.BOOTSTRAP], priorities=[1000]) # run before every other listener

    def _is_bootstrap_scenario(self, context: EventContext) -> bool:
      """Check if this is system bootstrap."""
      context = context.context
      try:
          bootstrap_address = self.address_generator.generate_bootstrap_address()
          entries = context.get_state([bootstrap_address])
          return len(entries) == 0
      except:
          return True
    
    def _mark_bootstrap_complete(self, event: EventContext):
      """Mark system bootstrap as complete."""
      bootstrap_address = self.address_generator.generate_bootstrap_address()
      context = event.context
      bootstrap_data = {
          'completed': True,
          'superadmin': event.signer_public_key,
          'timestamp': event.timestamp
      }
      context.set_state({
          bootstrap_address: self.serializer.to_bytes(bootstrap_data)
      })    

    def on_event(self, event: EventContext):
        # Handle bootstrap event
        # Create an admin account with super admin permissions
        # other admin accounts can be created later by this super admin

        if not self._is_bootstrap_scenario(event):
            raise InvalidTransaction("Bootstrap can only be performed once.")

        email = event.payload.get("email")
        assert email, "Email is required for bootstrap admin account."

        # Create a default super admin account
        account = AdminAccount(
            permission_level=AdminPermissionLevel.SUPER_ADMIN,
            public_key=event.signer_public_key,
            email=email,
            authentication_status=AuthenticationStatus.APPROVED,
            created_timestamp=event.timestamp,
            about="Initial super admin account created during system bootstrap. Holds all permissions. Use wisely.",
        )

        account.history.append({
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": ["bootstrap", account.public_key],
            "transaction": event.signature,
            "timestamp": event.timestamp
        })

        account_address = self.address_generator.generate_account_address(account.public_key)
        serialized_account = self.serialize_for_state(account)
        event.context.set_state({account_address: serialized_account})

        self._mark_bootstrap_complete(event)



