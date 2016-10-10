=====================================================
Checkbox Enhancement Proposal 8: Certification Status
=====================================================

Summary
=======

This proposal defines a way to add *whitelist* a.k.a. *blocker* or *graylist*
a.k.a. *non-blocker* classification to each job, in the sense used by the
Canonical Certification Team and to make it possible to surface this
information in test reports.

Glossary
========

test plan:
 An object describing which jobs to run that may carry additional meta-data.
whitelist:
 An object describing which jobs to run that cannot carry any additional
 meta-data. In the past this term was also informally used refer to *blocker
 status* of *blocker*.
certification status:
 Name of the new, proposed attribute that can be associated with a job
 definition within a testing session to clearly state how failure of that test
 will affect the overall certification process. Four values are possible:
 *unspecified*, *not-part-of-certification, *non-blocker* and *blocker*. The
 default value is *unspecified*. They are described below. Certification status
 may be defined on each job definition. It may also be overridden on a
 per-*test plan*-basis.
unspecified:
 One of the new possible certification status values. This value means that a
 job was not analyzed in the context of certification status classification and
 it has no classification at this time. This is also the implicit blocker
 status for all jobs.
not-part-of-certification:
 One of the new possible certification status values. This value means that a
 given job may fail and this will not affect the certification process in any
 way. Typically jobs with this certification status are not executed during the
 certification process. In the past this was informally referred to as a
 *blacklist item*.
non-blocker:
 One of the new possible certification status values. This value means that a
 given job may fail and while that should be regarded as a possible future
 problem it will not block the certification process. In the past this was
 informally referred to as a *graylist item*. Canonical reserves the right to
 promote jobs from the *non-blocker* to *blocker*.
blocker:
 One of the new possible certification status values. This value means that a
 given job must pass for the certification process to succeed. In the past this
 was informally referred to as a *whitelist item*. The term *blocker* was
 chosen to disambiguate the meaning of the two concepts.

Rationale
=========

The certification process is closely tied to the severity of the failure of
each test.  Currently this is informally specified in the testing guide. The
guide is not a machine readable document and it must be read and correctly
understood by each person participating in the testing and certification
process.

It is our wish to simplify this so that the information can be provided
automatically by Plainbox Providers and surfaced in appropriate user interfaces
to aid certificate reviewers and the Canonical Driver Test Suite consumers to
quickly get a yes-or-no answer without additional manual cross-checking.

Example Application (Certification)
===================================

A machine was tested with a test plan (or a whitelist), for client (laptop and
desktop) certification for Ubuntu 14.04. The test plan is composed of numerous
tests, each test is somehow associated with a ``certification-status``.

A submission is made to the certification website. The submission is composed
of (roughly) a list of results for each element in the test plan (using any of
the OUTCOME_xxx values, including OUTCOME_NONE). The reviewer needs to check if
a passing certificate can be issued. Instead of using their experience and
double checking the certification and testing guide, the reviewer can quickly
look at a single machine analysis of all of the results.

Since each result sent to the certification website is accompanied by the
certification status the certification website can quickly compute the overall
status of the submission. If there are any jobs with ``certification-status``
*blocker* that didn't pass (including the fact that a given test didn't run at
all) a failing certificate must be issued, otherwise a passing certificate may
be issued.

Example Application (CDTS)
==========================

A driver developer used test plan for upcoming LTS release to evaluate bleeding
edge code. The generated report contains simple classification on the quality
of the driver and if this code could pass subsequent certification testing as a
part of a complete product.

The same logic present in the HEXR certificate review process can be easily
replicated in any report since all of the data is available locally from the
test provider.

Additional Syntax
=================

There are three new bits of syntax available:
- a job definition unit can now have the ``certification-status`` field with
  all of the values listed above.
- a test plan unit can now have a new override section,
  ``certification-status-override`` which behaves identically to the other
  override section, category-overrides.
- a test plan can now use compact include-override syntax (see below) 

Example Syntax (Job Definition, common-field)
---------------------------------------------

The following example shows how we could assign certification status to a given
job using the job-definition-carries-data idea:

    id: job-1
    unit: job
    certification-status: non-blocker 

This example job (``job-1``) has two certification status associations.  One
for the 12.04 release (non-blocker) and another one for the 14.04 release
(blocker). Implicitly, this also carries to 14.10 and subsequent releases.

Jobs without an explicitly-assigned certification status will simply get the
*unspecified* certification status. It is expected that all important jobs are
modified to carry it though.

Example Syntax (Test Plan, override field)
------------------------------------------

The following example uses the ``override-*field*`` syntax to change the value
of the ``certification-status`` field for a given pattern. This mode is
preferred when the set of mask selection patterns and override patterns is
largely disjoint as it allows the reader to clearly see the overrides being
applied.

    id: job-1
    unit: job
    certification-status: non-blocker

    id: ubuntu-client-12.04
    unit: test plan
    include:
        job-1

    id: ubuntu-client-14.04
    unit: test plan
    include:
        job-1
    certification-status-overrides:
        apply blocker to job-1

Here to base job has a natural ``certification-status`` of *non-blocker*. The
``ubuntu-client-12.04`` test plan doesn't change that. The
``ubuntu-client-14.04`` test plan does, however, making the effective value
*blocker*.

Example Syntax (Test Plan, compact include-override)
----------------------------------------------------

The following example uses a more compact syntax which uses the ``include``
field to apply overrides and mask selection in one step. This is the preferred
way to make such changes, as the (perhaps long) list of mask selection patterns
does not need to be maintained in synchronization to the list of overrides.

    id: job-1
    unit: job
    certification-status: non-blocker

    id: ubuntu-client-12.04
    unit: test plan
    include:
        job-1

    id: ubuntu-client-14.04
    unit: test plan
    include:
        job-1 certification-status=blocker

Here to base job has a natural blocker status of *non-blocker*. The
``ubuntu-client-12.04`` test plan doesn't change that. The
``ubuntu-client-14.04`` test plan does, however, making the effective blocker
status *blocker*.

Historic Notes
==============

During the development of this CEP we were considering two variants, simplified
and complete. The simplified version didn't require additional internal API
changes. The simplified version would have required us to add the certification
blocker status data to each job. The complete version allowed us to put the
same data in a test plan instead. In the end we have selected the complete
version and went ahead with unifying test plans and whitelists internally.

Impact
======

Proposing this changes has the following impact on the Certification and QA
teams. Note that there are two versions, depending on the approach we take (see
implementation details below)

Impact (simplified version)
---------------------------

* The testing guide is no longer the reference, authoritative source of data
  for what constitutes the set of requirements for a given release of Ubuntu on
  a given form factor. Instead, this data is now available as a part of a test
  plan and can be automatically harvested and exported into composite
  documents.
* Plainbox models the appropriate information on a JobDefinition level.
  Appropriate certification status classification is manually added to
  all the job definitions using the testing guide as reference.
* HEXR needs to model the additional data and present it in the certificate
  review views. The actual views in HEXR need to be designed but at the very
  least we should provide a list of results, with the certification-status-per-result
  data available, as well as the effective certification status (which
  contains the collapsed result for the whole test plan)

Impact (complete version)
-------------------------

This is an extension to the simplified version:

* Plainbox needs to complete the transition to using test plans internally and
  to up-convert all whitelist files to test plans (in-memory) so that all data
  is available throughout the process.
* Plainbox models the appropriate information on a JobDefinition unit level and
  on the TestPlan level. Appropriate documentation is expanded to describe
  that. Plainbox carries the test plan information along to the exporter and
  report generation phase, as appropriate. Plainbox provides certification
  blocker status and effective test session certification status data
  in the XML exporter to be consumed by HEXR and the HTML report.

Implementation Details
======================

Two ideas
---------

During early discussion we came up with two possible implementation approaches:

- Implement this as a new set of fields (one per release) on a job definition.
  Test plans won't be a part of the picture (easier) and instead everything
  gets specified as a set of fields on particular jobs. The fields would allow
  us to put different certification status for the same job for different
  Ubuntu releases.
- Implement this just as we've implemented categories (as a both job and test
  plan concept). There we expect to provide a baseline in job definition and to
  fine-tune the details via certification status overrides inside each test
  plan (separately for each release).


TODO List for the complete (test plan based) variant
----------------------------------------------------

* We need to model the blocker status on the job and test plan unit, adding
  appropriate APIs where needed. We need to adjust documentation to the test
  plan and job units.
* We need to complete the transition to test plans internally, in the API, so
  that we have only (hopefully) one concept and we can load "test plans" from
  legacy whitelist files.
* We need to adjust all of the available reports, except for XML and HTML, to
  make use of the new information. This involves making test plan data available
  in the session somewhere so that it can be referenced.
* We need to update the checkbox-ng DBus bindings to work with test plans
  internally, masquerading them as whitelists in the API.
* We need to investigate the impact of the XML change on HEXR so that we can
  generate the HTML report. Alternatively, we can decouple those reports and
  adjust HTML separately.
* HEXR needs to be modified to model and display the blocker status association
  of each test. Note that this may change from submission to submission.

Open Questions
==============

It is unclear how the form factor concept will alter this plan. Going forward
Ubuntu will ship a single converged image that offers different functionality
depending on the (dynamic) form factor of the device. There the simple
per-release classification may be insufficient. At the same time we don't know
what the testing guide will be like for future releases so we cannot take any
action yet.
