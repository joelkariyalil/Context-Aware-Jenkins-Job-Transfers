Known Issues
============

This page tracks known issues, defects, and enhancements for the **Context Aware Jenkins Job Transfers** module. If you encounter any other issues, feel free to report them via our GitHub repository.

Abbreviations
-------------

.. list-table:: 
   :header-rows: 1
   :widths: 20 80

   * - Abbreviation
     - Meaning

   * - DF
     - Defect

   * - IS
     - Issue

   * - EH
     - Enhancement


Known Issues and Enhancements
-----------------------------

.. list-table:: 
   :header-rows: 1
   :widths: 10 10 50 15 15

   * - ID
     - Type
     - Description
     - Status
     - Workaround

   * - #001
     - EH
     - Time Consuming Processes
     - Open
     - Multi-threading Could be used to keep track of changing factors like Jobs/Views. Hence run-time compute would be a simple-lookup w/o having to ping the servers for responses.

   * - #002
     - IS
     - Plugins Don't Get Installed/Reloaded
     - Closed
     - Restart the jenkins server for changes to be Reloaded.

   * - #003
     - EH
     - Terminal Window a little cluttered
     - Open
     - Better design the terminal window outputs.


How to Report an Issue
----------------------

If you encounter an issue not listed here, please report it on our GitHub repository under the **Issues** section.

Thank you for your contributions in helping us improve this module!
