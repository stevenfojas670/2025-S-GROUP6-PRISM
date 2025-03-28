# PRISM PR Checklist 
The following is a checklist for doing PR reviews.

## 1. PR Overview
- [ ] Was the PR template followed?
- [ ] Did they go into enough detail for each section?
- [ ] Are there screenshots to visually show what their code does?
- [ ] Did they provide sufficient documentation?
- [ ] If applicable, did they discuss how to use their code?

## 2. Commits & Files
- [ ] If applicable, did they make sure to update the configuration files?
- [ ] If applicable, did they make sure to include any new dependencies?
- [ ] Do their commits indicate what changes they made to the files?
- [ ] Are all files related to the PR they are trying to make?
- [ ] Do their files have any documentation (i.e. comments)?
- [ ] Is their code readable, clean, and easy to follow?
- [ ] Are there any merge conflicts?
  - [ ] If so, can you resolve them?
     
## 3. Unit Testing
- [ ] Did they do any unit testing for their code?
- [ ] Did they indicate if they did manual tests on their own machine?
- [ ] Does their code pass the tests specified in GitHub Actions?
- [ ] Are the unit tests applicable to the code they wrote?
- [ ] Do the unit tests show their application working in all scenarios?
- [ ] Are there any missing unit tests that should be present?

## 4. Final Checks
- [ ] If applicable, does the PR satisfactory resolve the issue it's trying to fix?
- [ ] If the PR deletes any files, are the files being deleted needed still?
- [ ] If the PR adds files, are these files compatiable with the rest of the files?

Please consider all of these checks when writing your PR reviews in the future. 

If you are the second member to review a PR and the PR submitter is not waiting for another reviewer to get back to them, you may go ahead and approve the merge. If all reviews have occurred, then you are also allowed to merge and close the PR yourself. 
