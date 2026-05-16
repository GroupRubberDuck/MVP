// Seleziona il database che vuoi usare (verrà creato in automatico)
db = db.getSiblingDB('mvp_db');

// Inserisci i dati di partenza in una collection (es. 'utenti' o 'configurazioni')
db.compliance_standards.insertOne(
        {
    "_id": "EVS-EN_18031-1:2024-----",
    "name": "EVS-EN_18031",
    "version_number": "1:2024",
    "requirements": [
        {
            "id": "ACM-1",
            "name": "Applicability of access control mechanisms",
            "description": {
                "norm_description": "Determines if an access control mechanism must be in place to manage entities' access to the asset based on its accessibility and environment.",
                "target_description": "All Security and Network assets identified in the device that are accessible by entities."
            },
            "dependency_ids": [],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Is the public accessibility of the asset the equipment's intended functionality",
                        "child_yes": "leaf_na_1",
                        "child_no": "DN-2"
                    },
                    {
                        "node_id": "DN-2",
                        "node_type": "decision_node",
                        "question": "Do the physical or logical measures in the targeted operational environment limit the accessibility to authorized entities",
                        "child_yes": "leaf_na_2",
                        "child_no": "DN-3"
                    },
                    {
                        "node_id": "DN-3",
                        "node_type": "decision_node",
                        "question": "Do legal implications not allow access control mechanisms",
                        "child_yes": "leaf_na_3",
                        "child_no": "DN-4"
                    },
                    {
                        "node_id": "DN-4",
                        "node_type": "decision_node",
                        "question": "Are there access control mechanisms that manage entities' access to the security assets and network assets",
                        "child_yes": "leaf_pass_1",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_na_1",
                        "node_type": "leaf_node",
                        "verdict": "not_applicable"
                    },
                    {
                        "node_id": "leaf_na_2",
                        "node_type": "leaf_node",
                        "verdict": "not_applicable"
                    },
                    {
                        "node_id": "leaf_na_3",
                        "node_type": "leaf_node",
                        "verdict": "not_applicable"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "ACM-2",
            "name": "Appropriate access control mechanisms",
            "description": {
                "norm_description": "Ensures that access control mechanisms are effective in restricting access only to authorized entities.",
                "target_description": "Access control mechanisms identified in ACM-1."
            },
            "dependency_ids": [
                "ACM-1"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Do the access control mechanisms ensure that only authorized entities have access to the protected security asset or network asset",
                        "child_yes": "leaf_pass_1",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-1-1",
            "name": "Applicability of authentication mechanisms - Network interface",
            "description": {
                "norm_description": "Determines if authentication is required for network functions performed over network interfaces.",
                "target_description": "Network interfaces and related network function configurations."
            },
            "dependency_ids": [
                "ACM-1"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Is the absence of authentication required for the equipment's intended functionality",
                        "child_yes": "leaf_pass_1",
                        "child_no": "DN-2"
                    },
                    {
                        "node_id": "DN-2",
                        "node_type": "decision_node",
                        "question": "Is the access performed over networks where access is limited to authorized entities",
                        "child_yes": "leaf_pass_2",
                        "child_no": "DN-3"
                    },
                    {
                        "node_id": "DN-3",
                        "node_type": "decision_node",
                        "question": "Does the managed access use authentication mechanisms",
                        "child_yes": "leaf_pass_3",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_pass_2",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_pass_3",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-1-2",
            "name": "Applicability of authentication mechanisms - User interface",
            "description": {
                "norm_description": "Determines if authentication is required for access via physical or logical user interfaces.",
                "target_description": "User interfaces (local or remote) and associated network function configurations."
            },
            "dependency_ids": [
                "ACM-1"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Do physical or logical measures in the targeted environment provide confidence in the correctness of an entity's claim",
                        "child_yes": "leaf_pass_1",
                        "child_no": "DN-2"
                    },
                    {
                        "node_id": "DN-2",
                        "node_type": "decision_node",
                        "question": "Is access without authentication needed to enable intended equipment functionality",
                        "child_yes": "leaf_pass_2",
                        "child_no": "DN-3"
                    },
                    {
                        "node_id": "DN-3",
                        "node_type": "decision_node",
                        "question": "Is access without authentication mandated by legal implications",
                        "child_yes": "leaf_na_1",
                        "child_no": "DN-4"
                    },
                    {
                        "node_id": "DN-4",
                        "node_type": "decision_node",
                        "question": "Does the managed access use authentication mechanisms",
                        "child_yes": "leaf_pass_3",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_pass_2",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_na_1",
                        "node_type": "leaf_node",
                        "verdict": "not_applicable"
                    },
                    {
                        "node_id": "leaf_pass_3",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-2-NI",
            "name": "Appropriate authentication mechanisms - Network",
            "description": {
                "norm_description": "Ensures the authentication mechanism uses at least one factor for authentication of entities (knowledge, possession, or inherence).",
                "target_description": "Authentication mechanisms identified for network interfaces in AUM-1-1."
            },
            "dependency_ids": [
                "AUM-1-1"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Does the authentication mechanism examine evidence from at least one category (knowledge, possession, inherence)",
                        "child_yes": "leaf_pass_1",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-2-UI",
            "name": "Appropriate authentication mechanisms - User",
            "description": {
                "norm_description": "Ensures the authentication mechanism uses at least one factor for authentication of entities (knowledge, possession, or inherence).",
                "target_description": "Authentication mechanisms identified for user interfaces in AUM-1-2."
            },
            "dependency_ids": [
                "AUM-1-2"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Does the authentication mechanism examine evidence from at least one category (knowledge, possession, inherence)",
                        "child_yes": "leaf_pass_1",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-3-NI",
            "name": "Authenticator validation - Network",
            "description": {
                "norm_description": "Ensures the authentication mechanism validates all relevant properties of the authenticator in the operational environments of use.",
                "target_description": "Authentication mechanisms identified for network interfaces in AUM-1-1."
            },
            "dependency_ids": [
                "AUM-1-1"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Does the mechanism validate all relevant properties of the authenticator in its operational environment",
                        "child_yes": "leaf_pass_1",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-3-UI",
            "name": "Authenticator validation - User",
            "description": {
                "norm_description": "Ensures the authentication mechanism validates all relevant properties of the authenticator in the operational environments of use.",
                "target_description": "Authentication mechanisms identified for user interfaces in AUM-1-2."
            },
            "dependency_ids": [
                "AUM-1-2"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Does the mechanism validate all relevant properties of the authenticator in its operational environment",
                        "child_yes": "leaf_pass_1",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-4-NI",
            "name": "Changing authenticators - Network",
            "description": {
                "norm_description": "Verifies that the authentication mechanism allows the authenticator factor to be changed by an authorized entity, unless it conflicts with security goals.",
                "target_description": "Authentication mechanisms identified for network interfaces in AUM-1-1."
            },
            "dependency_ids": [
                "AUM-1-1"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Does changing the authenticator conflict with security goals",
                        "child_yes": "leaf_na_1",
                        "child_no": "DN-2"
                    },
                    {
                        "node_id": "DN-2",
                        "node_type": "decision_node",
                        "question": "Does the authentication mechanism allow the change of the authenticator",
                        "child_yes": "leaf_pass_1",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_na_1",
                        "node_type": "leaf_node",
                        "verdict": "not_applicable"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-4-UI",
            "name": "Changing authenticators - User",
            "description": {
                "norm_description": "Verifies that the authentication mechanism allows the authenticator factor to be changed by an authorized entity, unless it conflicts with security goals.",
                "target_description": "Authentication mechanisms identified for user interfaces in AUM-1-2."
            },
            "dependency_ids": [
                "AUM-1-2"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Does changing the authenticator conflict with security goals",
                        "child_yes": "leaf_na_1",
                        "child_no": "DN-2"
                    },
                    {
                        "node_id": "DN-2",
                        "node_type": "decision_node",
                        "question": "Does the authentication mechanism allow the change of the authenticator",
                        "child_yes": "leaf_pass_1",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_na_1",
                        "node_type": "leaf_node",
                        "verdict": "not_applicable"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-5-1-NI",
            "name": "Password strength - factory default passwords - Network",
            "description": {
                "norm_description": "Ensures factory default passwords are changed before or on first use, or that they are unique per device and follow best practices regarding strength.",
                "target_description": "Factory default passwords used by authentication mechanisms for network interfaces in AUM-1-1."
            },
            "dependency_ids": [
                "AUM-1-1"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Is the password enforced to be changed by the user before or on first use",
                        "child_yes": "leaf_pass_1",
                        "child_no": "DN-2"
                    },
                    {
                        "node_id": "DN-2",
                        "node_type": "decision_node",
                        "question": "Is the password unique per equipment",
                        "child_yes": "DN-3",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "DN-3",
                        "node_type": "decision_node",
                        "question": "Does the password follow best practice concerning strength",
                        "child_yes": "leaf_pass_2",
                        "child_no": "leaf_fail_2"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    },
                    {
                        "node_id": "leaf_pass_2",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_2",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-5-1-UI",
            "name": "Password strength - factory default passwords - User",
            "description": {
                "norm_description": "Ensures factory default passwords are changed before or on first use, or that they are unique per device and follow best practices regarding strength.",
                "target_description": "Factory default passwords used by authentication mechanisms for user interfaces in AUM-1-2."
            },
            "dependency_ids": [
                "AUM-1-2"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Is the password enforced to be changed by the user before or on first use",
                        "child_yes": "leaf_pass_1",
                        "child_no": "DN-2"
                    },
                    {
                        "node_id": "DN-2",
                        "node_type": "decision_node",
                        "question": "Is the password unique per equipment",
                        "child_yes": "DN-3",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "DN-3",
                        "node_type": "decision_node",
                        "question": "Does the password follow best practice concerning strength",
                        "child_yes": "leaf_pass_2",
                        "child_no": "leaf_fail_2"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    },
                    {
                        "node_id": "leaf_pass_2",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_2",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-5-2-NI",
            "name": "Password strength - non-factory default passwords - Network",
            "description": {
                "norm_description": "Validates that non-factory passwords are set securely before first usenetwork connection, defined by an authorized entity, or generated securely by the device.",
                "target_description": "Non-factory default passwords used by authentication mechanisms for network interfaces in AUM-1-1."
            },
            "dependency_ids": [
                "AUM-1-1"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Is the password enforced to be set by the user before first use and before network connection",
                        "child_yes": "leaf_pass_1",
                        "child_no": "DN-2"
                    },
                    {
                        "node_id": "DN-2",
                        "node_type": "decision_node",
                        "question": "Is the password defined by an authorized entity within a protected network",
                        "child_yes": "leaf_pass_2",
                        "child_no": "DN-3"
                    },
                    {
                        "node_id": "DN-3",
                        "node_type": "decision_node",
                        "question": "Is the password generated by the equipment using best practices and communicated securely",
                        "child_yes": "leaf_pass_3",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_pass_2",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_pass_3",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-5-2-UI",
            "name": "Password strength - non-factory default passwords - User",
            "description": {
                "norm_description": "Validates that non-factory passwords are set securely before first usenetwork connection, defined by an authorized entity, or generated securely by the device.",
                "target_description": "Non-factory default passwords used by authentication mechanisms for user interfaces in AUM-1-2."
            },
            "dependency_ids": [
                "AUM-1-2"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Is the password enforced to be set by the user before first use and before network connection",
                        "child_yes": "leaf_pass_1",
                        "child_no": "DN-2"
                    },
                    {
                        "node_id": "DN-2",
                        "node_type": "decision_node",
                        "question": "Is the password defined by an authorized entity within a protected network",
                        "child_yes": "leaf_pass_2",
                        "child_no": "DN-3"
                    },
                    {
                        "node_id": "DN-3",
                        "node_type": "decision_node",
                        "question": "Is the password generated by the equipment using best practices and communicated securely",
                        "child_yes": "leaf_pass_3",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_pass_2",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_pass_3",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-6-NI",
            "name": "Brute force protection - Network",
            "description": {
                "norm_description": "Ensures the authentication mechanism has protection mechanisms against brute force attacks.",
                "target_description": "Authentication mechanisms identified for network interfaces in AUM-1-1."
            },
            "dependency_ids": [
                "AUM-1-1"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Is the authentication mechanism resilient against brute force attacks",
                        "child_yes": "leaf_pass_1",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        },
        {
            "id": "AUM-6-UI",
            "name": "Brute force protection - User",
            "description": {
                "norm_description": "Ensures the authentication mechanism has protection mechanisms against brute force attacks.",
                "target_description": "Authentication mechanisms identified for user interfaces in AUM-1-2."
            },
            "dependency_ids": [
                "AUM-1-2"
            ],
            "decision_tree": {
                "root_node_id": "DN-1",
                "nodes": [
                    {
                        "node_id": "DN-1",
                        "node_type": "decision_node",
                        "question": "Is the authentication mechanism resilient against brute force attacks",
                        "child_yes": "leaf_pass_1",
                        "child_no": "leaf_fail_1"
                    },
                    {
                        "node_id": "leaf_pass_1",
                        "node_type": "leaf_node",
                        "verdict": "pass"
                    },
                    {
                        "node_id": "leaf_fail_1",
                        "node_type": "leaf_node",
                        "verdict": "fail"
                    }
                ]
            }
        }
    ]
}
)