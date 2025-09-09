# Marker Implementation

This document describes marker implementation following LD-3.4 specification.

## LD-3.4 Compliance

This implementation follows the LD-3.4 specification for marker processing.

## Pipeline Stages

The marker pipeline processes text through these stages:

1. **ATO** detection
2. **SEM** grouping  
3. **CLU** clustering
4. **MEMA** memory formation

## Cross-References

For terminology, see [terminologie.md](terminologie.md).
For system overview, see [architecture.md](architecture.md).

## Processing Flow

Each `me process` command follows this workflow:

- Input validation
- ATO extraction
- SEM formation from ATO groups
- CLU clustering of SEM units
- MEMA pattern detection