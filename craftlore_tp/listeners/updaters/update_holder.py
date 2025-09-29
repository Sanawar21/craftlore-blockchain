from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.assets import Certification
from models.enums import EventType

class CertificateHolderUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.CERTIFICATION_ISSUED],
            priorities=[-200]
        )  # default priority

    def on_event(self, event: EventContext):
        certificate: Certification = event.get_data("entity")
        certificate_address = event.get_data("entity_address")

        if not certificate or not certificate_address:
            raise InvalidTransaction("Certificate data or address not found in event context for UpdateCertificateHolder")
        if "-" in certificate.holder:
            holder, holder_address = self.get_asset(certificate.holder, event)
            targets = [certificate.uid, holder.uid]
        else:
            holder, holder_address = self.get_account(certificate.holder, event)
            targets = [certificate.uid, holder.public_key]

        holder.certifications.append(certificate.uid)
        holder.history.append({
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": targets,
            "transaction": event.signature,
            "timestamp": event.timestamp
        })
        event.context.set_state({
            holder_address: self.serialize_for_state(holder)
        })
        event.add_data({
            "holder_address": holder_address,
            "holder": holder,
            "admin": event.get_data("owner"),
            "admin_address": event.get_data("owner_address")
        })
