# Synthetic Process Glossary

> Synthetic-only document. The terms below are invented labels for software tests and do not define a real semiconductor process vocabulary.

| Term | Synthetic meaning |
| --- | --- |
| demo pressure target | A fictional numeric field used to exercise a target parameter with unit Pa. The value is not a process limit. |
| demo source power | A fictional numeric field used to exercise a setpoint parameter with unit W. The value is not a recipe setting. |
| parameter drift marker | An invented event label showing that a synthetic measurement differs from a fictional target. It is not a failure mechanism. |
| unresolved value | A data-quality state in which the example does not support a reliable normalized value. |
| not-applicable value | A state used when the fictional scenario does not call for a value of that type. |
| synthetic document chunk | A bounded text fragment retained with an invented document identifier and location for future retrieval tests. |

## Usage boundary

These definitions are intentionally narrow. They help tests compare stable strings and labels. They must not be used to infer production terminology, metrology practice, equipment behavior, or process-control decisions.

Every term, number, and relationship in this glossary is fictional.
