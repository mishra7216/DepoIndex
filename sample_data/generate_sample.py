"""
DepoIndex – Synthetic sample deposition PDF generator.

Creates a realistic 20-page deposition transcript PDF for demo and testing.
Topics covered span multiple pages, with topic returns and digressions.

Usage:
    python sample_data/generate_sample.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make sure reportlab is importable
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
except ImportError:
    print("reportlab not installed. Run: pip install reportlab")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Deposition transcript content
# ---------------------------------------------------------------------------

# Each item: (transcript_page_number, list_of_lines)
# Lines: (line_number, speaker, text)  speaker: "Q" | "A" | "" (header/blank)

DEPOSITION_CONTENT = [
    # -----------------------------------------------------------------------
    # Page 1 – Cover / Caption
    # -----------------------------------------------------------------------
    (1, [
        (0,  "",  "IN THE UNITED STATES DISTRICT COURT"),
        (0,  "",  "FOR THE NORTHERN DISTRICT OF CALIFORNIA"),
        (0,  "",  ""),
        (0,  "",  "ACME TECHNOLOGIES INC.,"),
        (0,  "",  "       Plaintiff,"),
        (0,  "",  "vs.                                Case No. 3:25-CV-01234-JD"),
        (0,  "",  "VERTEX SOLUTIONS LLC,"),
        (0,  "",  "       Defendant."),
        (0,  "",  ""),
        (0,  "",  "DEPOSITION OF MICHAEL HARTWELL"),
        (0,  "",  ""),
        (0,  "",  "DATE: February 14, 2025"),
        (0,  "",  "LOCATION: Conference Room B, 450 Market Street, San Francisco, CA"),
        (0,  "",  "TAKEN BY: Plaintiff's Counsel"),
    ]),
    # -----------------------------------------------------------------------
    # Page 2 – Appearances
    # -----------------------------------------------------------------------
    (2, [
        (0,  "",  "APPEARANCES:"),
        (0,  "",  ""),
        (0,  "",  "For the Plaintiff:"),
        (0,  "",  "  JENNIFER PARK, ESQ."),
        (0,  "",  "  Goldstein & Park LLP"),
        (0,  "",  "  500 California Street, Suite 1200"),
        (0,  "",  "  San Francisco, CA 94111"),
        (0,  "",  ""),
        (0,  "",  "For the Defendant:"),
        (0,  "",  "  RAYMOND COLBY, ESQ."),
        (0,  "",  "  Colby & Simmons LLP"),
        (0,  "",  "  One Embarcadero Center, Suite 800"),
        (0,  "",  "  San Francisco, CA 94111"),
        (0,  "",  ""),
        (0,  "",  "Also Present: Court Reporter – Sandra Tran"),
    ]),
    # -----------------------------------------------------------------------
    # Page 3 – Oath and personal background
    # -----------------------------------------------------------------------
    (3, [
        (1,  "",  "EXAMINATION BY MS. PARK:"),
        (2,  "Q", "Please state your full name for the record."),
        (3,  "A", "Michael James Hartwell."),
        (4,  "Q", "And what is your current home address?"),
        (5,  "A", "742 Evergreen Terrace, Palo Alto, California, 94301."),
        (6,  "Q", "How long have you lived at that address?"),
        (7,  "A", "About six years. We moved there in early 2019."),
        (8,  "Q", "Are you married?"),
        (9,  "A", "Yes. Married for eleven years."),
        (10, "Q", "Do you have children?"),
        (11, "A", "Two daughters, ages eight and five."),
        (12, "Q", "Mr. Hartwell, have you ever given a deposition before?"),
        (13, "A", "No. This is the first time."),
        (14, "Q", "I'll explain the ground rules briefly. You've been sworn in."),
        (15, "A", "Understood."),
        (16, "Q", "If you don't understand a question, please ask me to repeat it."),
        (17, "A", "I will. Thank you."),
        (18, "Q", "Let's begin with your educational background."),
        (19, "A", "Sure."),
        (20, "Q", "Where did you attend college?"),
        (21, "A", "I received my bachelor's degree from UCLA in computer science,"),
        (22, "A", "graduating in 2003. Then I completed a master's degree at"),
        (23, "A", "Stanford University in electrical engineering in 2005."),
        (24, "Q", "Did you have any relevant certifications after graduate school?"),
        (25, "A", "Yes. I obtained a Project Management Professional certification"),
    ]),
    # -----------------------------------------------------------------------
    # Page 4 – Education continued → Employment
    # -----------------------------------------------------------------------
    (4, [
        (1,  "A", "in 2007 through the PMI organization."),
        (2,  "Q", "Did you pursue any other formal education after that?"),
        (3,  "A", "No additional degrees. I attended several executive leadership"),
        (4,  "A", "seminars over the years, but nothing degree-granting."),
        (5,  "Q", "Thank you. Now let's talk about your employment history."),
        (6,  "A", "Of course."),
        (7,  "Q", "What was your first position after completing graduate school?"),
        (8,  "A", "I joined Hewlett-Packard as a software engineer in 2005."),
        (9,  "Q", "How long were you at Hewlett-Packard?"),
        (10, "A", "Three years. From 2005 to 2008."),
        (11, "Q", "What was your role there?"),
        (12, "A", "I was a software engineer initially, then promoted to senior"),
        (13, "A", "software engineer in my second year."),
        (14, "Q", "And after Hewlett-Packard?"),
        (15, "A", "I moved to Oracle Corporation in 2008. I was a principal"),
        (16, "A", "software architect there for four years."),
        (17, "Q", "Did you have any managerial responsibilities at Oracle?"),
        (18, "A", "Yes, from 2010 onward I managed a team of twelve engineers."),
        (19, "Q", "What happened after Oracle?"),
        (20, "A", "I joined Acme Technologies in 2012 as their VP of Engineering."),
        (21, "Q", "And Acme Technologies is the plaintiff in this case?"),
        (22, "A", "That's correct."),
        (23, "Q", "When did you leave Acme Technologies?"),
        (24, "A", "My employment ended in September 2024."),
        (25, "Q", "Under what circumstances did your employment end?"),
    ]),
    # -----------------------------------------------------------------------
    # Page 5 – Employment end / Company structure begins
    # -----------------------------------------------------------------------
    (5, [
        (1,  "A", "I resigned. It was a mutual separation. I submitted a formal"),
        (2,  "A", "resignation letter and the board accepted it."),
        (3,  "Q", "Were there any negotiations regarding the terms of your departure?"),
        (4,  "A", "There was a separation agreement. I had counsel review it."),
        (5,  "Q", "We'll return to that agreement later. Let me ask you about"),
        (6,  "Q", "the company structure at Acme Technologies."),
        (7,  "A", "All right."),
        (8,  "Q", "Who was the CEO of Acme Technologies during your tenure?"),
        (9,  "A", "Sandra Kim was the CEO from 2010 through 2023. After her"),
        (10, "A", "retirement, David Chu became CEO in January 2024."),
        (11, "Q", "To whom did you report?"),
        (12, "A", "I reported directly to Sandra Kim, and after her retirement,"),
        (13, "A", "to David Chu."),
        (14, "Q", "How many direct reports did you have?"),
        (15, "A", "Four. The directors of product engineering, infrastructure,"),
        (16, "A", "quality assurance, and data science each reported to me."),
        (17, "Q", "Was there a board of directors?"),
        (18, "A", "Yes. A seven-member board."),
        (19, "Q", "Did you ever attend board meetings?"),
        (20, "A", "Quarterly, yes. I presented the engineering roadmap."),
        (21, "Q", "Now I'd like to ask you about your relationship with"),
        (22, "Q", "Vertex Solutions, the defendant in this case."),
        (23, "A", "I'll do my best to answer."),
        (24, "Q", "When did you first become aware of Vertex Solutions?"),
        (25, "A", "Approximately in mid-2022, through a mutual business contact."),
    ]),
    # -----------------------------------------------------------------------
    # Page 6 – Business relationships
    # -----------------------------------------------------------------------
    (6, [
        (1,  "Q", "Who was that contact?"),
        (2,  "A", "A colleague named Brian Okafor. He introduced me to"),
        (3,  "A", "Patricia Nguyen, who was VP of Sales at Vertex Solutions."),
        (4,  "Q", "What was the nature of that initial introduction?"),
        (5,  "A", "Strictly professional. Brian thought there might be a"),
        (6,  "A", "potential partnership opportunity between the two companies."),
        (7,  "Q", "Did Acme Technologies and Vertex Solutions ever enter into"),
        (8,  "Q", "a formal business relationship?"),
        (9,  "A", "Yes. We signed a technology licensing agreement in March 2023."),
        (10, "Q", "Who signed on behalf of Acme Technologies?"),
        (11, "A", "I signed, along with Sandra Kim and our general counsel,"),
        (12, "A", "Robert Marsh."),
        (13, "Q", "I'm going to show you what has been marked Exhibit 3."),
        (14, "Q", "Is this the licensing agreement you just described?"),
        (15, "A", "Yes. This is the agreement. I recognize my signature on page eight."),
        (16, "Q", "What were the core terms of this agreement?"),
        (17, "A", "Vertex licensed three of our proprietary software modules"),
        (18, "A", "for a three-year term, for which they paid an upfront fee"),
        (19, "A", "and quarterly royalties based on deployment counts."),
        (20, "Q", "What was the upfront fee?"),
        (21, "A", "Two million dollars."),
        (22, "Q", "And the quarterly royalty rate?"),
        (23, "A", "Four percent of net revenue attributable to the licensed modules."),
        (24, "Q", "When was the first royalty payment due?"),
        (25, "A", "June 30, 2023, for the first quarter after the agreement."),
    ]),
    # -----------------------------------------------------------------------
    # Page 7 – Financial transactions
    # -----------------------------------------------------------------------
    (7, [
        (1,  "Q", "Did Vertex Solutions make that first royalty payment?"),
        (2,  "A", "No. They did not."),
        (3,  "Q", "When did you first become aware that payment was not made?"),
        (4,  "A", "Around July 8, 2023. Our finance director notified me."),
        (5,  "Q", "Who is your finance director?"),
        (6,  "A", "Helen Farrow."),
        (7,  "Q", "Did you receive any communication from Vertex Solutions"),
        (8,  "Q", "about the missed payment?"),
        (9,  "A", "Patricia Nguyen sent me an email on July 10, 2023 stating"),
        (10, "A", "that they were experiencing cash flow issues and requesting"),
        (11, "A", "a sixty-day extension."),
        (12, "Q", "I'll show you Exhibit 4. Is this the email you described?"),
        (13, "A", "Yes. That's correct."),
        (14, "Q", "Did Acme Technologies grant the extension?"),
        (15, "A", "I consulted with Sandra Kim and Robert Marsh. We agreed to"),
        (16, "A", "a forty-five day extension, not sixty."),
        (17, "Q", "Was Vertex notified of the approved extension period?"),
        (18, "A", "Yes. Robert Marsh sent a formal letter, Exhibit 5, on July 15."),
        (19, "Q", "Did Vertex make the payment within the extended period?"),
        (20, "A", "They made a partial payment of $190,000 on August 28, 2023."),
        (21, "Q", "What was the full amount owed at that point?"),
        (22, "A", "Approximately $480,000 including the accrued royalties."),
        (23, "Q", "So there remained an outstanding balance of approximately"),
        (24, "Q", "$290,000?"),
        (25, "A", "That's approximately correct, yes."),
    ]),
    # -----------------------------------------------------------------------
    # Page 8 – Financial transactions continued / Communications
    # -----------------------------------------------------------------------
    (8, [
        (1,  "Q", "What happened after the partial payment in August 2023?"),
        (2,  "A", "We sent formal notices. Robert Marsh sent a notice of default"),
        (3,  "A", "in September 2023."),
        (4,  "Q", "Did you personally communicate with anyone at Vertex after"),
        (5,  "Q", "the default notice?"),
        (6,  "A", "Yes. I had several phone calls with Patricia Nguyen and"),
        (7,  "A", "also one call with their CEO, Marcus Trent."),
        (8,  "Q", "Approximately when was the call with Marcus Trent?"),
        (9,  "A", "October 2023. I believe October 14th."),
        (10, "Q", "What was discussed during that call?"),
        (11, "A", "He proposed restructuring the payment schedule. He suggested"),
        (12, "A", "spreading the remaining balance over twelve months."),
        (13, "Q", "Did Acme agree to that proposal?"),
        (14, "A", "We did not agree at that time. We needed board approval."),
        (15, "Q", "Let me shift topics briefly to the communications you had"),
        (16, "Q", "with Patricia Nguyen via email. Do you recall approximately"),
        (17, "Q", "how many emails you exchanged with her?"),
        (18, "A", "Over the entire relationship, probably forty to fifty emails."),
        (19, "Q", "Did you save copies of those emails?"),
        (20, "A", "They would be in our corporate email system. I don't believe"),
        (21, "A", "I deleted any of them."),
        (22, "Q", "Were these emails produced in discovery?"),
        (23, "A", "I believe our IT team exported the full thread, yes."),
        (24, "Q", "Good. Let me now ask you about a specific meeting that"),
        (25, "Q", "occurred on November 5, 2023."),
    ]),
    # -----------------------------------------------------------------------
    # Page 9 – Meetings
    # -----------------------------------------------------------------------
    (9, [
        (1,  "A", "Yes. The in-person meeting at our offices."),
        (2,  "Q", "Who attended that meeting?"),
        (3,  "A", "From Acme: myself, Sandra Kim, Robert Marsh, and Helen Farrow."),
        (4,  "A", "From Vertex: Marcus Trent, Patricia Nguyen, and their CFO,"),
        (5,  "A", "Thomas Birch."),
        (6,  "Q", "Was there an agenda for the meeting?"),
        (7,  "A", "Yes. Sandra circulated an agenda the day before via email."),
        (8,  "Q", "I'll show you Exhibit 7. Is this the agenda?"),
        (9,  "A", "Yes, that's it."),
        (10, "Q", "The agenda references a 'restructuring proposal.' What does"),
        (11, "Q", "that refer to?"),
        (12, "A", "It refers to Vertex's proposed twelve-month payment plan for"),
        (13, "A", "the outstanding balance."),
        (14, "Q", "Was any agreement reached at the November 5th meeting?"),
        (15, "A", "Not formally. Vertex presented revised financial projections."),
        (16, "A", "We agreed to consider their proposal and respond within two weeks."),
        (17, "Q", "Were minutes taken at the meeting?"),
        (18, "A", "Yes. Our general counsel's office prepared meeting minutes."),
        (19, "Q", "Were those minutes circulated to Vertex?"),
        (20, "A", "Yes, I believe so. They were sent to Marcus Trent for review."),
        (21, "Q", "Did Marcus Trent respond to the minutes?"),
        (22, "A", "He sent a brief email noting one correction regarding a figure."),
        (23, "Q", "What was the correction?"),
        (24, "A", "He said the outstanding balance figure in the minutes was"),
        (25, "A", "incorrect. He stated it should be $285,000, not $290,000."),
    ]),
    # -----------------------------------------------------------------------
    # Page 10 – Documents and records
    # -----------------------------------------------------------------------
    (10, [
        (1,  "Q", "Do you know which figure was correct?"),
        (2,  "A", "Helen Farrow confirmed after the meeting that the correct"),
        (3,  "A", "amount was $287,500 as of that date, factoring in interest."),
        (4,  "Q", "Were there any other documents exchanged at or after"),
        (5,  "Q", "the November 5th meeting?"),
        (6,  "A", "Vertex sent us a formal restructuring proposal document"),
        (7,  "A", "on November 20, 2023. It was about fourteen pages."),
        (8,  "Q", "I'm showing you Exhibit 9. Is this that proposal?"),
        (9,  "A", "Yes. This is the document."),
        (10, "Q", "Did Acme formally respond to Exhibit 9?"),
        (11, "A", "We sent a counter-proposal on December 5, 2023."),
        (12, "Q", "Was that counter-proposal accepted by Vertex?"),
        (13, "A", "No. They rejected two key terms."),
        (14, "Q", "What were those terms?"),
        (15, "A", "First, we required a personal guarantee from Marcus Trent."),
        (16, "A", "Second, we required a security interest in their primary"),
        (17, "A", "server infrastructure as collateral."),
        (18, "Q", "Did Vertex provide any written response to those requirements?"),
        (19, "A", "Their counsel sent a letter in December refusing both terms."),
        (20, "Q", "I'd like to return to the financial transactions for a moment."),
        (21, "Q", "Were there any payments made after August 2023?"),
        (22, "A", "Yes. Two additional small payments. $30,000 in December 2023"),
        (23, "A", "and $25,000 in February 2024."),
        (24, "Q", "So the remaining balance in early 2024 was approximately"),
        (25, "Q", "$232,500?"),
    ]),
    # -----------------------------------------------------------------------
    # Page 11 – Financial transactions return / Specific incidents
    # -----------------------------------------------------------------------
    (11, [
        (1,  "A", "That's approximately right. Subject to interest calculations."),
        (2,  "Q", "Did Acme Technologies ever send a formal demand letter"),
        (3,  "Q", "threatening litigation?"),
        (4,  "A", "Yes. In March 2024, Robert Marsh sent a sixty-day demand letter."),
        (5,  "Q", "I'm showing you Exhibit 12. Is this the demand letter?"),
        (6,  "A", "Yes. That's the letter."),
        (7,  "Q", "What response, if any, did Acme receive?"),
        (8,  "A", "Vertex's outside counsel responded by letter. They disputed"),
        (9,  "A", "the royalty calculations and claimed the agreement was"),
        (10, "A", "ambiguous regarding the definition of net revenue."),
        (11, "Q", "I'd like to ask you about a specific incident in May 2024."),
        (12, "Q", "Are you aware of an unauthorized access to Acme's source code"),
        (13, "Q", "repository in May 2024?"),
        (14, "A", "I am aware that an incident occurred. Our security team"),
        (15, "A", "detected anomalous access patterns on May 7, 2024."),
        (16, "Q", "What was the nature of those access patterns?"),
        (17, "A", "Someone accessed the private repository for Module 2,"),
        (18, "A", "which was one of the modules licensed to Vertex, using"),
        (19, "A", "credentials that had been revoked six months earlier."),
        (20, "Q", "Whose credentials were used?"),
        (21, "A", "The credentials belonged to a former Vertex contractor who"),
        (22, "A", "had worked on the integration project in 2022 and 2023."),
        (23, "Q", "Was this reported to law enforcement?"),
        (24, "A", "Yes. We notified the FBI's Cyber Division in May 2024."),
        (25, "Q", "Was any data confirmed to have been taken?"),
    ]),
    # -----------------------------------------------------------------------
    # Page 12 – Specific incident continued / key people
    # -----------------------------------------------------------------------
    (12, [
        (1,  "A", "Our forensic team concluded that approximately 1.2 gigabytes"),
        (2,  "A", "of source code was exfiltrated during the incident."),
        (3,  "Q", "Was Vertex Solutions informed of this incident?"),
        (4,  "A", "Their counsel was notified in June 2024 via letter."),
        (5,  "Q", "Did Vertex respond to that notification?"),
        (6,  "A", "Yes. They denied any involvement and offered to cooperate"),
        (7,  "A", "with the investigation."),
        (8,  "Q", "I'd like to ask you about some of the individuals involved"),
        (9,  "Q", "in this matter. Who is Brian Okafor?"),
        (10, "A", "Brian Okafor is a technology consultant based in San Jose."),
        (11, "A", "He's known both me and Patricia Nguyen professionally for"),
        (12, "A", "several years. He facilitated the initial introduction."),
        (13, "Q", "Does Brian Okafor have any financial interest in either"),
        (14, "Q", "Acme Technologies or Vertex Solutions?"),
        (15, "A", "Not to my knowledge."),
        (16, "Q", "Who is Patricia Nguyen?"),
        (17, "A", "She's the VP of Sales at Vertex Solutions. She was my primary"),
        (18, "A", "point of contact throughout the business relationship."),
        (19, "Q", "Is she still employed at Vertex?"),
        (20, "A", "I believe so, yes."),
        (21, "Q", "Who is Marcus Trent?"),
        (22, "A", "Marcus Trent is the CEO of Vertex Solutions."),
        (23, "Q", "Have you had any personal communication with Marcus Trent"),
        (24, "Q", "outside of official business matters?"),
        (25, "A", "No. Our interactions were strictly professional."),
    ]),
    # -----------------------------------------------------------------------
    # Page 13 – Key people / separation agreement (contracts)
    # -----------------------------------------------------------------------
    (13, [
        (1,  "Q", "Who is Robert Marsh?"),
        (2,  "A", "Robert Marsh is the General Counsel at Acme Technologies."),
        (3,  "Q", "Who is Thomas Birch?"),
        (4,  "A", "Thomas Birch is the CFO of Vertex Solutions."),
        (5,  "Q", "Now let's return to your separation from Acme Technologies."),
        (6,  "Q", "You mentioned a separation agreement. Do you still have"),
        (7,  "Q", "a copy of that agreement?"),
        (8,  "A", "I have a copy, yes. My attorney retains the original."),
        (9,  "Q", "I'm showing you Exhibit 14. Is this your separation agreement?"),
        (10, "A", "Yes. This is the document."),
        (11, "Q", "The agreement contains a non-disparagement clause. Correct?"),
        (12, "A", "Yes."),
        (13, "Q", "And a non-compete clause?"),
        (14, "A", "Yes. A twelve-month non-compete from the date of separation."),
        (15, "Q", "Have you complied with that non-compete clause?"),
        (16, "A", "I have. I haven't taken employment in the same sector."),
        (17, "Q", "Were there any financial terms in the separation agreement?"),
        (18, "A", "There was a severance payment. Four months' base salary."),
        (19, "Q", "What was your base salary at the time of separation?"),
        (20, "A", "Three hundred and forty thousand dollars per year."),
        (21, "Q", "So the severance payment was approximately $113,000?"),
        (22, "A", "Approximately, yes."),
        (23, "Q", "Were there any equity-related provisions?"),
        (24, "A", "My unvested stock options were addressed. They were forfeited"),
        (25, "A", "per the standard vesting agreement terms."),
    ]),
    # -----------------------------------------------------------------------
    # Page 14 – Contracts continued / Employment history return
    # -----------------------------------------------------------------------
    (14, [
        (1,  "Q", "Were there any conditions attached to the severance payment?"),
        (2,  "A", "The standard conditions: execution of the agreement, release"),
        (3,  "A", "of claims, compliance with the non-compete and confidentiality."),
        (4,  "Q", "Did you negotiate any terms of the separation agreement?"),
        (5,  "A", "My attorney negotiated the length of the non-compete. It was"),
        (6,  "A", "originally proposed as eighteen months. We got it reduced to twelve."),
        (7,  "Q", "Was the severance amount negotiated?"),
        (8,  "A", "No. The four-month severance was standard per Acme policy."),
        (9,  "Q", "Let me go back to your employment history for a moment."),
        (10, "Q", "Before joining Acme Technologies, did you have any consulting"),
        (11, "Q", "engagements?"),
        (12, "A", "Briefly. Between Oracle and Acme, from January to June 2012,"),
        (13, "A", "I worked independently as a technology consultant."),
        (14, "Q", "Who were your clients during that period?"),
        (15, "A", "Primarily small to mid-size software companies in the Bay Area."),
        (16, "Q", "Did you have any clients that were in the same industry"),
        (17, "Q", "as Acme Technologies?"),
        (18, "A", "One client was in adjacent space. Data analytics. Not directly"),
        (19, "A", "competitive with Acme's products at the time."),
        (20, "Q", "What is that company's name?"),
        (21, "A", "Meridian Analytics. They were acquired by Salesforce in 2017."),
        (22, "Q", "After Acme Technologies, have you had any employment?"),
        (23, "A", "I've been on a sabbatical. Spending time with family and"),
        (24, "A", "considering my next move."),
        (25, "Q", "Are you under any NDA restrictions that would prevent you"),
    ]),
    # -----------------------------------------------------------------------
    # Page 15 – Digression / Wrap-up
    # -----------------------------------------------------------------------
    (15, [
        (1,  "Q", "from discussing the technical details of Acme's software?"),
        (2,  "A", "The separation agreement has a confidentiality clause."),
        (3,  "A", "My counsel advised me on the scope."),
        (4,  "Q", "I want to ask you a few questions about your personal use"),
        (5,  "Q", "of Acme's equipment. Did you use a company laptop?"),
        (6,  "A", "Yes. I returned it upon separation."),
        (7,  "Q", "Did you use a company phone?"),
        (8,  "A", "Yes. Also returned."),
        (9,  "Q", "Did you ever use your personal devices to access Acme systems?"),
        (10, "A", "Occasionally. For convenience when traveling."),
        (11, "Q", "Did you ever store Acme confidential documents on your"),
        (12, "Q", "personal devices?"),
        (13, "A", "Not intentionally. I may have had email attachments cached"),
        (14, "A", "on my personal phone."),
        (15, "Q", "Have you deleted any Acme documents from your personal devices"),
        (16, "Q", "since your separation?"),
        (17, "A", "I performed a factory reset of my personal phone as part of"),
        (18, "A", "normal maintenance in October 2024."),
        (19, "Q", "Was that before or after you received notice of this litigation?"),
        (20, "A", "I received the litigation notice in November 2024. The reset"),
        (21, "A", "was in October, before that notice."),
        (22, "Q", "Let me take a short break. We'll resume in five minutes."),
        (23, "A", "Of course."),
        (24, "",  "(RECESS TAKEN)"),
        (25, "",  "(DEPOSITION RESUMED)"),
    ]),
    # -----------------------------------------------------------------------
    # Page 16 – Email communications (return)
    # -----------------------------------------------------------------------
    (16, [
        (1,  "Q", "Back on the record. Mr. Hartwell, I want to return to"),
        (2,  "Q", "the email communications between you and Patricia Nguyen."),
        (3,  "A", "Yes."),
        (4,  "Q", "I'm going to show you Exhibit 16, which is a printed"),
        (5,  "Q", "email thread. Please review it."),
        (6,  "A", "I've looked at it."),
        (7,  "Q", "Does this email chain accurately reflect your correspondence"),
        (8,  "Q", "with Patricia Nguyen between January and June 2024?"),
        (9,  "A", "It appears to, yes."),
        (10, "Q", "I'd like to draw your attention to the email on page three"),
        (11, "Q", "of the exhibit, dated March 18, 2024. Did you write this email?"),
        (12, "A", "Yes, I did."),
        (13, "Q", "You wrote, and I quote: 'Patricia, I want to be clear that"),
        (14, "Q", "if full payment is not received by April 30, we will have no"),
        (15, "Q", "choice but to pursue formal remedies.' Is that accurate?"),
        (16, "A", "Yes. That reflects our position at the time."),
        (17, "Q", "Did Patricia Nguyen respond to that email?"),
        (18, "A", "Yes. She responded the same day, asking for a phone call."),
        (19, "Q", "Did that phone call take place?"),
        (20, "A", "Yes. On March 19, 2024."),
        (21, "Q", "What was discussed?"),
        (22, "A", "She reiterated Vertex's position that the royalty calculation"),
        (23, "A", "methodology was disputed. She said they'd commissioned an"),
        (24, "A", "independent audit of the figures."),
        (25, "Q", "Did that audit ever materialize?"),
    ]),
    # -----------------------------------------------------------------------
    # Page 17 – Communications continued
    # -----------------------------------------------------------------------
    (17, [
        (1,  "A", "We never received any audit report from Vertex."),
        (2,  "Q", "How did Acme respond to the disputed royalty calculation claim?"),
        (3,  "A", "Our finance team prepared a detailed breakdown supporting"),
        (4,  "A", "our figures. Robert Marsh sent it to Vertex's counsel in April 2024."),
        (5,  "Q", "Was that breakdown accepted by Vertex?"),
        (6,  "A", "No. Their counsel maintained the dispute."),
        (7,  "Q", "I'd like to ask you about your conversations with David Chu,"),
        (8,  "Q", "who became CEO in January 2024. Did David Chu take an active"),
        (9,  "Q", "role in the Vertex matter?"),
        (10, "A", "Yes. He was briefed in January 2024 and was involved in all"),
        (11, "A", "major decisions from that point forward."),
        (12, "Q", "Did David Chu ever communicate directly with anyone at Vertex?"),
        (13, "A", "He and Marcus Trent exchanged two or three emails in early 2024."),
        (14, "Q", "Did you review those emails?"),
        (15, "A", "I was copied on them, yes."),
        (16, "Q", "What was the nature of those emails?"),
        (17, "A", "David was trying to explore whether a commercial resolution"),
        (18, "A", "was possible before litigation. It was not successful."),
        (19, "Q", "When did Acme Technologies decide to file the complaint?"),
        (20, "A", "The board authorized litigation in August 2024."),
        (21, "Q", "Were you involved in that decision?"),
        (22, "A", "I was still employed in August. I participated in the"),
        (23, "A", "strategy discussions, yes."),
        (24, "Q", "Did you provide any input to outside counsel in preparing"),
        (25, "Q", "the complaint?"),
    ]),
    # -----------------------------------------------------------------------
    # Page 18 – Legal proceedings / Company structure return
    # -----------------------------------------------------------------------
    (18, [
        (1,  "A", "I provided factual context. I was interviewed by outside"),
        (2,  "A", "counsel twice before I departed Acme."),
        (3,  "Q", "When were those interviews?"),
        (4,  "A", "Once in August and once in early September 2024."),
        (5,  "Q", "Were you represented by counsel during those interviews?"),
        (6,  "A", "Not during the interviews themselves. I consulted with"),
        (7,  "A", "my personal attorney after the second interview."),
        (8,  "Q", "Since leaving Acme, have you communicated with anyone at"),
        (9,  "Q", "Acme about this litigation?"),
        (10, "A", "Robert Marsh called me twice to clarify factual matters."),
        (11, "Q", "What was discussed in those calls?"),
        (12, "A", "Details about meeting dates and specific document histories."),
        (13, "Q", "Let me turn to the company structure at Vertex Solutions."),
        (14, "Q", "Based on your dealings with them, can you describe what you"),
        (15, "Q", "know about their corporate structure?"),
        (16, "A", "Only from external dealings. They appeared to have a"),
        (17, "A", "relatively flat structure. Marcus Trent as CEO, Thomas Birch"),
        (18, "A", "as CFO, Patricia Nguyen as VP Sales. They had a technical team"),
        (19, "A", "but I never met those people directly."),
        (20, "Q", "Did Vertex Solutions have a board of directors?"),
        (21, "A", "I assume so, but I have no direct knowledge of their governance."),
        (22, "Q", "Did you ever meet anyone representing Vertex's investors?"),
        (23, "A", "No."),
        (24, "Q", "Do you know if Vertex Solutions is privately held?"),
        (25, "A", "I believe they are, yes. Privately held."),
    ]),
    # -----------------------------------------------------------------------
    # Page 19 – Wrap-up questions
    # -----------------------------------------------------------------------
    (19, [
        (1,  "Q", "Are you aware of any other agreements between Acme and Vertex"),
        (2,  "Q", "beyond the March 2023 licensing agreement?"),
        (3,  "A", "No other formal agreements. There were discussions about"),
        (4,  "A", "a potential reseller arrangement in late 2023, but those"),
        (5,  "A", "discussions did not lead to a signed agreement."),
        (6,  "Q", "Who led those discussions on Acme's side?"),
        (7,  "A", "Patricia Nguyen approached me about it. I involved our"),
        (8,  "A", "VP of Business Development, Leon Vasquez."),
        (9,  "Q", "And those discussions were ultimately abandoned?"),
        (10, "A", "Yes. By early 2024 the payment dispute had soured the relationship."),
        (11, "Q", "Mr. Hartwell, to the best of your knowledge, is there any"),
        (12, "Q", "information we have not discussed today that would be relevant"),
        (13, "Q", "to the claims in this case?"),
        (14, "A", "Nothing comes to mind. I've tried to be as complete as possible."),
        (15, "Q", "I want to give defense counsel an opportunity to ask questions."),
        (16, "",  "EXAMINATION BY MR. COLBY:"),
        (17, "Q", "Mr. Hartwell, how would you characterize the overall business"),
        (18, "Q", "relationship with Vertex Solutions before the payment dispute?"),
        (19, "A", "It was professional and cooperative. We believed it was a"),
        (20, "A", "mutually beneficial arrangement."),
        (21, "Q", "Did Vertex ever fail to comply with any technical obligations"),
        (22, "Q", "under the licensing agreement?"),
        (23, "A", "Not to my knowledge. The dispute was purely financial."),
        (24, "Q", "Is it possible the royalty calculation methodology was"),
        (25, "Q", "genuinely ambiguous?"),
    ]),
    # -----------------------------------------------------------------------
    # Page 20 – Closing
    # -----------------------------------------------------------------------
    (20, [
        (1,  "A", "I think the language was clear. But I acknowledge that"),
        (2,  "A", "reasonable people might read it differently. That's why"),
        (3,  "A", "we're here."),
        (4,  "Q", "Thank you. No further questions from defense."),
        (5,  "",  "EXAMINATION BY MS. PARK:"),
        (6,  "Q", "Just a few follow-up questions. Did Acme's finance team"),
        (7,  "Q", "rely on Vertex's self-reported deployment numbers?"),
        (8,  "A", "For the first two quarters, yes. By Q3 2023 we requested"),
        (9,  "A", "verification and Vertex provided a certification letter."),
        (10, "Q", "Do you have any reason to believe Vertex underreported"),
        (11, "Q", "its deployment numbers?"),
        (12, "A", "I have no confirmed evidence of that. It was a concern."),
        (13, "Q", "That's all I have. Thank you, Mr. Hartwell."),
        (14, "A", "Thank you."),
        (15, "",  "(DEPOSITION CONCLUDED)"),
        (16, "",  ""),
        (17, "",  "CERTIFICATE OF REPORTER"),
        (18, "",  ""),
        (19, "",  "I, Sandra Tran, Certified Court Reporter, certify that the"),
        (20, "",  "foregoing is a true and accurate transcript of the deposition"),
        (21, "",  "of Michael James Hartwell, taken on February 14, 2025."),
        (22, "",  ""),
        (23, "",  "________________________"),
        (24, "",  "Sandra Tran, CCR No. 5921"),
        (25, "",  "Date: February 28, 2025"),
    ]),
]


def generate_deposition_pdf(output_path: str = "sample_data/sample_deposition.pdf") -> str:
    """
    Generate a synthetic deposition transcript PDF.

    Returns the path to the generated file.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.lib import colors

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # Styles
    header_style = ParagraphStyle(
        "Header",
        fontName="Helvetica-Bold",
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    line_style = ParagraphStyle(
        "Line",
        fontName="Courier",
        fontSize=9,
        leading=13,
        leftIndent=0,
        spaceAfter=0,
    )
    page_num_style = ParagraphStyle(
        "PageNum",
        fontName="Helvetica-Bold",
        fontSize=9,
        alignment=TA_CENTER,
        spaceBefore=6,
        spaceAfter=6,
    )

    story = []

    for transcript_page, content_lines in DEPOSITION_CONTENT:
        # Page number header
        story.append(Paragraph(str(transcript_page), page_num_style))

        for line_no, speaker, text in content_lines:
            if not text and not speaker:
                story.append(Spacer(1, 4))
                continue
            if line_no == 0:
                # Non-numbered line (headers, captions, etc.)
                para = Paragraph(text, header_style)
            else:
                if speaker:
                    formatted = f"{line_no:>2}   {speaker}.  {text}"
                else:
                    formatted = f"{line_no:>2}        {text}"
                para = Paragraph(formatted.replace("&", "&amp;").replace("<", "&lt;"), line_style)
            story.append(para)

        story.append(Spacer(1, 20))  # gap between transcript pages

    doc.build(story)
    print(f"Sample deposition PDF created: {output.resolve()}")
    return str(output.resolve())


if __name__ == "__main__":
    generate_deposition_pdf()
