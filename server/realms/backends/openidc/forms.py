from django import forms
from realms.forms import RealmForm


class OpenIDConnectRealmForm(RealmForm):
    discovery_url = forms.URLField(required=True)
    client_id = forms.CharField(required=True)
    client_secret = forms.CharField(
        required=False,
        help_text="Optional client secret if needed. If not set, a PKCE challenge will be used"
    )
    extra_scopes = forms.CharField(
        required=False,
        help_text="Comma separated list of extra scopes (like email, profile, …)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            for attr in ("discovery_url", "client_id", "client_secret", "extra_scopes"):
                val = self.instance.config.get(attr)
                if val:
                    if attr == "extra_scopes":
                        val = ", ".join(val)
                    self.fields[attr].initial = val

    def clean_extra_scopes(self):
        extra_scopes = self.cleaned_data.get("extra_scopes")
        if extra_scopes:
            extra_scopes = [s for s in (s.strip() for s in extra_scopes.split(",")) if s]
        return extra_scopes

    def get_config(self):
        config = {}
        for attr in ("discovery_url", "client_id", "client_secret", "extra_scopes"):
            val = self.cleaned_data.get(attr)
            if val is not None:
                config[attr] = val
        return config
