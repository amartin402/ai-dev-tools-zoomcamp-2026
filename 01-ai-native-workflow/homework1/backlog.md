# Backlog

Each task is intentionally scoped to one working session. A task includes enough context and acceptance criteria to be assigned without requiring the assignee to read another task first.

## 1. Set up an empty Django project

Create the Django project with `uv`, add the application package, register the app, and keep the project free of product features. Add one basic test proving the Django test suite runs successfully.

Acceptance criteria:

- Dependencies are declared in `pyproject.toml` and locked with `uv.lock`.
- `uv run python manage.py check` succeeds.
- `uv run python manage.py test` succeeds with at least one passing test.
- The application is registered in `INSTALLED_APPS`.

## 2. Add a project model and project list

Implement the project entity that groups recurring feedback cycles. Include a name, optional description, creator, and timestamps. Add a page that lists projects and a form for creating one.

Acceptance criteria:

- Projects can be created through the Django application.
- The project list displays the project name and creation date.
- Model, form, view, and URL tests cover successful creation and listing.

## 3. Add project membership and facilitator roles

Allow users to belong to projects and distinguish regular team members from facilitators. A project creator must be a facilitator, and a project page must show its members and roles.

Acceptance criteria:

- A user can be added to a project with a member or facilitator role.
- The project creator is represented as a facilitator.
- Membership changes are restricted to project facilitators.
- Tests cover role assignment and unauthorized membership changes.

## 4. Build the project dashboard

Create the project page described in the plan. Show the current feedback cycle, submission status, upcoming or active retrospective, previous retrospectives, and open action items using empty states where data does not exist yet.

Acceptance criteria:

- An authenticated project member can open the project dashboard.
- Each planned dashboard section has a clear empty state.
- A user cannot view a project dashboard unless they belong to the project.
- Tests cover member access and non-member denial.

## 5. Create and manage weekly feedback cycles

Implement feedback cycles belonging to one project. A facilitator can create, open, and close a cycle with a title, description, start date, and end date.

Acceptance criteria:

- A cycle cannot exist without a project.
- Only facilitators can create, open, or close cycles.
- A project shows its current open cycle and past closed cycles.
- Tests cover the lifecycle and facilitator-only permissions.

## 6. Submit private Start, Stop, and Continue cards

Implement separate feedback cards for the three categories in the plan. A team member can add multiple cards to an open cycle and choose whether each card is attributed or anonymous.

Acceptance criteria:

- Each card belongs to exactly one cycle and one category: Start, Stop, or Continue.
- A member can submit multiple cards in each category.
- Empty card content is rejected.
- Tests cover valid submission, category validation, and membership requirements.

## 7. Enforce feedback visibility and editing rules

Restrict feedback access before the retrospective begins. Contributors can view and edit only their own cards, while facilitators and other members cannot inspect unrevealed cards. Anonymous cards must not expose their author in any user-facing response.

Acceptance criteria:

- A contributor can edit and delete their own card before reveal.
- A contributor cannot edit another contributor’s card.
- Unrevealed cards are not visible to other members or facilitators.
- Anonymous cards render without author information.
- Tests cover every visibility and mutation rule.

## 8. Start a retrospective and reveal feedback

Add a retrospective record for a feedback cycle and implement facilitator-controlled state transitions for starting the retrospective and revealing all submitted cards at once.

Acceptance criteria:

- A retrospective belongs to one feedback cycle and cannot belong to multiple projects.
- Only a facilitator can start or reveal it.
- Cards remain hidden until the reveal transition completes.
- Invalid state transitions are rejected and tested.

## 9. Create editable feedback clusters

Allow revealed cards to be grouped into named clusters. Team members can move cards between clusters, leave cards ungrouped, and facilitators can rename, merge, or split clusters.

Acceptance criteria:

- A cluster belongs to one retrospective.
- A revealed card can belong to zero or one cluster.
- Cluster names can be edited, and empty clusters can be removed.
- Permissions match the collaboration rules and are covered by tests.

## 10. Add editable automatic-clustering proposals

Create a clustering proposal interface that can suggest groups without finalizing them. Store proposals separately from accepted clusters so a facilitator can accept, edit, or discard them.

Acceptance criteria:

- A proposal is visibly distinct from an accepted cluster.
- Applying a proposal never prevents manual card movement or renaming.
- Discarding a proposal leaves accepted clusters unchanged.
- Tests cover proposal creation, application, editing, and discard behavior.

## 11. Implement stackable voting with hidden totals

Give each project member three votes for a retrospective. Allow multiple votes on one cluster, hide totals while voting is open, and reveal ranked totals when everyone has voted or the facilitator closes voting.

Acceptance criteria:

- A member cannot cast more than three total votes.
- Multiple votes can target the same cluster.
- Vote totals are hidden before voting closes.
- Closing voting reveals clusters ordered by total votes.
- Tests cover vote limits, duplicate targeting, visibility, and close behavior.

## 12. Run the discussion agenda

Add the discussion mode for the ranked clusters. A facilitator can mark each topic as discussed, skipped, or deferred and record notes, decisions, and proposed action items.

Acceptance criteria:

- Discussion topics follow the finalized voting order.
- Each topic has exactly one of the three discussion statuses or remains pending.
- Members can add notes; facilitator-only controls are protected.
- Tests cover status transitions and permissions.

## 13. Track action items

Implement action items with description, owner, optional due date, open or done status, and a related discussion topic. Support assignment during or after discussion.

Acceptance criteria:

- Every action item belongs to one retrospective discussion topic.
- An action item has an owner and defaults to Open.
- Assigned owners can mark their actions Done.
- Facilitators can edit action details and ownership.
- Tests cover creation, assignment, status updates, and permissions.

## 14. Capture meeting records and transcript text

Add a post-meeting upload page that accepts an audio file, video file, transcript file, or pasted transcript text. Track the record type and processing status without implementing transcription yet.

Acceptance criteria:

- A meeting record belongs to one retrospective.
- Exactly one supported input method is required per record.
- Facilitators can create and view records; other members cannot upload them.
- Processing status is visible and starts as pending.
- Tests cover input validation and facilitator-only access.

## 15. Store draft extracted outcomes

Add a provider-neutral service boundary and data models for transcript processing results: suggested decisions, action items, owners, due dates, and a short summary. Use a deterministic fake processor in tests instead of an external AI service.

Acceptance criteria:

- Processing a meeting record creates draft outcomes without publishing them.
- Draft actions include description, optional owner, optional due date, and related topic when available.
- Processing failures are represented by a failed status and user-visible error state.
- Tests use the fake processor and do not require network access.

## 16. Review and approve extracted outcomes

Build the facilitator review screen for draft decisions, action items, owners, due dates, and the summary. Facilitators can edit, approve, or reject each draft before it becomes part of the retrospective record.

Acceptance criteria:

- Draft outcomes are never displayed as confirmed outcomes.
- A facilitator can approve or reject each draft independently.
- Approved action items follow the normal action-item rules.
- Non-facilitators cannot approve, reject, or edit drafts.
- Tests cover independent review decisions and permissions.

## 17. Publish the retrospective summary

Create the completed retrospective summary page containing top discussion topics, notes, confirmed decisions, confirmed action items, participation, and original feedback cards.

Acceptance criteria:

- A facilitator can publish a summary only after the retrospective is complete.
- Unapproved extracted outcomes are excluded from the published summary.
- Project members can view a published summary but cannot edit it.
- Tests cover publication prerequisites, included sections, and read-only member access.

## 18. Add an end-to-end MVP workflow test

Exercise the complete happy path from project creation through cycle setup, feedback submission, reveal, clustering, voting, discussion, meeting record processing, outcome approval, and summary publication.

Acceptance criteria:

- The test uses Django’s test client and deterministic fixtures or fake processing.
- The complete workflow succeeds for a facilitator and at least two team members.
- The test verifies anonymous feedback remains anonymous.
- The test verifies only approved extracted outcomes appear in the published summary.
