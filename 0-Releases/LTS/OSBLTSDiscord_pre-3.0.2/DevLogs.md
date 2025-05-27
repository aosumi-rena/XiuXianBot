# Dev Logs
## 17 Jan 2025 Update
`SGCBDiscord_V-I3_0.1.2.11`-->`SGCBDiscord_V-I3_0.1.2.12`
1. Removed variation codes in version value
2. Added check for potential database error, will say "Database Error! Contact Bot admin!" when database has any type of error
## 25W04a Update (Released: 24 Jan 2025)
`SGCBDiscord_V-I3_0.1.2.12`-->`SGCBDiscord_i3.0.1.2.12_25W04a\*`
1. `hunt` cultivation gain `0.5%~1%` --> `0.75%~1.25%`
2. ~~`shop` command can view the shop (no actual function yet)~~ (Postponed to 25W04b)
3. Change in the inventory storing method, change in `inv` function's ui
## 25W04b Update (Released: 26 Jan 2025)
`SGCBDiscord_i3.0.1.2.12_25W04a\*`-->`SGCBDiscord_i3.0.1.3_25W04b\*`
1. ~~Fully functioning `shop` command~~ (Postponed to 25w05a)
2. DM commands (accounts related):
  - Using `/acc` to check account details, can change username and language
  - Redemption code ~~ui~~ actual function via `/acc` (additional button)
## 25w05a Update (Released: 29 Jan 2025)
`SGCBDiscord_i3.0.1.3_25W04b\*`-->`SGIBDiscord_i3.0.1.4_25w05a\*`
1. Standardisation of textmaps
2. Fully working `^shop` command (But no use cuz no useful items)
3. Fix found bugs
  - Textmap not loaded (no reminder for which key not loaded also) on `^inv` command

G1 (30 Jan 2025):
   1. Updated error responses.

G2 (31 Jan 2025):
   1. Fixed ultra rare bug for inv command errorly embedded

G3 (14 Feb 2025):
   1. Improved localisation for {items_section} for "redeem_code_success"
## 25w06a Update
There is no update this week
## 25w07a Update (Released: 14 Feb 2025)
`SGIBDiscord_i3.0.1.4_25w05a\*`→`SGIBDiscord_i3.0.1.7_25w07a\*`
1. Element cycle testing, each day has different element corresponding to it, use `^ele` or `^ele check` to check the element of the day
  - Element list:
      - Metallo
      - Dendro
      - Hydro
      - Pyro
      - Geo
3. Selecting elements (No actual uses yet), changing elements and cooldown testing, `^ele choose` to view element list and `^ele choose <num>` to choose element type
4. Preparing for code rewrite on adding mutiplicative zone for values

## 25w07b Update (Released: 16 Feb 2025)
`SGIBDiscord_i3.0.1.7_25w07a\*`→`SGIBDiscord_i3.0.1.7_25w07b\*`
1. Added viewing of user's element in ^stat and /acc view
2. Added cehck of whether user is cultivating when usimg ^ele choose <num>, so that sudden choosing will not bug the multiplication zone
3. Added localisation textmaps for element names

G1 (17 Feb 2025):
   1. Fixed localisation on ele_choose_success
## 25w08a Update (Released: 22 Feb 2025)
`SGIBDiscord_i3.0.1.7_25w07b\*`→`SGIBDiscord_i3.0.1.8_25w08a\*`
1. Code rewrite for multiplicative zone for most of possibly changable values
  - Rewriting values giving functions
  - Update textmaps to match, instead of fixed texts
2. Fully implant for elements cycle function (`^ele`)
  - Effect of elements (all non-int values will **round down**):
      - Same element:
        - 1.5 times cultivation gain for `^cul`
        - Double gain of "cppper" in `^hunt`
        - Double chance of getting "gold" in `^hunt`
        - Same cultivation gain for `^hunt`
        - Base chance for asc fail rate change to `8%`
      - Restrained element:
        - 0.75 times cultivation gain for `^cul`
        - 0.75 times gain of "cppper" in `^hunt`
        - No change in chance of getting "gold" in `^hunt`
        - 0.75 times cultivation gain for `^hunt`
        - Base chance for asc fail rate change to `15%`
      - Mutual element:
        - Double cultivation gain for `^cul`
        - 1.5 times gain of "cppper" in `^hunt`
        - No change in chance of getting "gold" in `^hunt`
        - Double times cultivation gain for `^hunt`
        - No change for base chance for asc fail rate (still `10%`)
  - Elements will have important use in future features like battling system
  - Changed base-culti gain for  `^cul` to random integer from `150 to 250`, this value is then used to calculate for elemental buff.

G1, G2 and G3 (22 Feb 2025):
   1. Fixed some found bug on element buff processing

G4 (22 Feb 2025):
   1. Added command `^ele rule(s)` to show rules for element buffing system
   
G5 (22 Feb 2025):
   1. Fixed error `NO_TEXT(cultivation_end)` when cultivation ends
## 25w09a Update (Released: 25 Feb 2025)
`SGIBDiscord_i3.0.1.8_25w08a\*`→`SGIBDiscord_i3.0.1.9_25w09a\*`
### Textmap Related
1. Fixed redeem_code_success still fall back to CHS
2. Fixed element name at `^ele` or `^ele check` still fall back to CHS
3. Fixed element main panel's textmap for function not updated for EN
### New Functions
1. `^contact` To show contacts of bot admins.
### Others
1. Added restriction to user name to limited to 40 characters.
## 25w10a Update (Released: 9 Mar 2025)
`SGIBDiscord_i3.0.1.9_25w09a\*`→`SGIBDiscord_i3.0.2_25w10a\*`
### Localisation
1. Fix localisation for element name at stat
2. AdminCommand: added indexing for textmap keys for `^a:text`
### Utilities
1. Changed the way of autosave for users' progress
2. Added autosaving for `items` collection
### Cultivation
1. Fixed that certain condition will cause cultivation gained default back to 200.

G1 (9 Mar 2025):
   1. Improved `^a:tm`'s UI

## Preview-LTS Release: `OSBLTSDiscord_pre-3.0.2`
1. First Preview-LTS version, a stabilised version based on `SGIBDiscord_i3.0.2_25w10a_G1`