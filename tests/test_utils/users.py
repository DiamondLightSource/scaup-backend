from lims_utils.auth import GenericUser

admin = GenericUser(
    permissions=["em_admin", "super_admin"],
    fedid="foo",
    id="foo",
    familyName="bar",
    title="Mr.",
    givenName="foo",
)

em_admin = GenericUser(
    permissions=["em_admin"],
    fedid="foo",
    id="foo",
    familyName="bar",
    title="Mr.",
    givenName="foo",
)

user = GenericUser(
    permissions=[],
    fedid="foo",
    id="foo",
    familyName="bar",
    title="Mr.",
    givenName="foo",
)
