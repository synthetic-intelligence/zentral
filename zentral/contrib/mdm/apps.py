from zentral.utils.apps import ZentralAppConfig


class ZentralMDMAppConfig(ZentralAppConfig):
    name = "zentral.contrib.mdm"
    default = True
    verbose_name = "Zentral MDM contrib app"
    permission_models = (
        "artifact",
        "asset",
        "blueprint",
        "depdevice",
        "depenrollment",
        "depvirtualserver",
        "deviceartifact",
        "enrolleddevice",
        "enrolleduser",
        "enterpriseapp",
        "profile",
        "pushcertificate",
        "otaenrollment",
        "scepconfig",
        "servertoken",
        "userartifact",
        "userenrollment",
    )
