# codeminer
Tool for analyzing code lineage

## Build Information
[![Build Status](https://travis-ci.org/jacobschaer/codeminer.svg?branch=master)](https://travis-ci.org/jacobschaer/codeminer)

## Motivation
At a previous job, an audit of intellectual property rights for software sparked an effort to determine the legacy of each file in our repositories. Unfortunately, the codebase has had many homes over the years including:

  * Concurrent Versions System (CVS)
  * Revision Control System (RCS)
  * Subversion (SVN)
  * Microsoft Visual Source Safe (VSS)
  * Simple file/folder organizations

Since each version control system has its own unique peculiarities, a great deal of effort was expended scraping and normalizing history information from each. While tools for individual repositories (typically converters) do exist, many are poorly maintained or bug-ridden. This project aims to provide a uniform interface for reading (and eventually writing) to such version control systems.

## Initial Goals:
  
  * Support reading/writing to Mercurial (Hg), Git, and SVN 
  * Support scraping file history into common database
  * Support basic commit analysis to simplify commit actions
    - Detect moves/copies where not directly implemented by repository
    - Detect compound changes like move/copy followed by modification

## Future Goals:

  * Support proprietary repositories such as VSS and Perforce
  * Support "legacy" repository types such as CVS and RCS
  * Support "advanced" commit analysis:
    - Detect lineage across commits and repositories
    - Rate similarity between two files for manual lineage adjustment
  * Full web-app