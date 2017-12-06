---
title: 'Category Encoders: a scikit-learn-contrib package of transformers for encoding categorical data'
tags:
  - machine learning
  - python
  - sckit-learn
authors:
 - name: William D McGinnis
   orcid: 0000-0002-3009-9465
   affiliation: "1, 2"
affiliations:
 - name: Predikto, Inc.
   index: 1
 - name: Helton Tech, LLC
   index: 2
date: 5 December 2017
bibliography: paper.bib
---

# Summary

Category_encoders is a scikit-learn-contrib module of transformers for encoding categorical data. As a scikit-learn-contrib
module, category_encoders is fully compatible with the scikit-learn API [@scikit-learn-api]. It also uses heavily the tools
provided by scikit-learn [@scikit-learn] itself, scipy[@scipy], pandas[@pandas], and statsmodels[@statsmodels].

It includes a number of pre-existing encoders that are commonly used, notably Ordinal, Hashing and OneHot encoders [@idre][@carey][@hashing]. There are also some
less frequently used encoders including Backward Difference, Helmert, Polynomial and Sum encoding [@idre][@carey]. Finally there are
experimental encoders: LeaveOneOut, Binary and BaseN [@zhang][@onehot][@basen].

The goal of these sorts of transforms is to represent categorical data, which has no true order, as numeric values while
balancing desires to keep the representation in as few dimensions as possible.  Category_encoders seeks to provide access
to the many methodologies for accomplishing such tasks in a simple to use, well tested, and production ready package.


# References

