# tournaments.fit

Since the [FIT Player Eligibility Policy](https://docs.internationaltouch.org/policy/player-eligibility/) has been amended, we need a new system to evaluate all the possible combinations of player eligibility, receive their declarations, and record acknowledgements from certified individuals that they have sighted documentation that is consistent with the declarations.

## How will it work?

A person who is interested in playing international Touch will need to signup and fill in a series of questions to build their profile.

This profile will be:

- their name, date of birth, country of birth, and country of residence
- their parents (biological or adoptive) details (name, date of birth, country of birth)
- their grandparents (parents biological or adoptive parent) details (name, date of birth, country of birth)

Once the profile is created, the person will be required to make their declarations in accordance with the policy.

The salient point is that prior to the closing date for final registrations for that event, the player must nominate which country they elect to play for at that event.

Further, Tier One Nations must declare which dual-qualified players are in their training squads (three months prior to final nominations) and then teams (two weeks prior to final nominations).

In order to facilitate this, only players who have made their declarations to align to a country will be able to be claimed, and only with a declaration by an official of the Tier One Nation that they've cited necessary documentation that corroborates the claim of eligibility.

## Prototype

The prototype is being implemented in the Django Admin. Operating at the data level only, without a guiding workflow, allows us to build out the necessary evaluation logic, but avoids the complexity of user experience.
