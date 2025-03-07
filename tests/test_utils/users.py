from lims_utils.auth import GenericUser

admin = GenericUser(
    permissions=["em_admin", "super_admin"],
    fedid="foo",
    id="foo",
    familyName="bar",
    title="Mr.",
    givenName="foo",
    email="test@diamond.ac.uk",
)

em_admin = GenericUser(
    permissions=["em_admin"],
    fedid="foo",
    id="foo",
    familyName="bar",
    title="Mr.",
    givenName="foo",
    email="test@diamond.ac.uk",
)

user = GenericUser(
    permissions=[], fedid="foo", id="foo", familyName="bar", title="Mr.", givenName="foo", email="test@diamond.ac.uk"
)
