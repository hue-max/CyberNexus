
"""Train a Random Forest threat classifier for CyberNexus.

The dataset is synthetic and intended for project prototyping.
Evaluate with real, labelled security data before production use.
"""

from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


DATA = [
    # Brute-force activity
    ("login_failure high repeated login failure", "brute_force"),
    ("authentication failed multiple password attempts", "brute_force"),
    ("security alert password guessing detected", "brute_force"),
    ("critical repeated attempts to guess account password", "brute_force"),
    ("many failed login attempts from same source", "brute_force"),
    ("repeated authentication failures user account", "brute_force"),
    ("suspicious repeated password attempts", "brute_force"),
    ("multiple failed logins within five minutes", "brute_force"),
    ("account locked after repeated incorrect credentials", "brute_force"),
    ("automated attempts to access account with passwords", "brute_force"),
    ("authentication rejected repeatedly from remote host", "brute_force"),
    ("several unsuccessful sign in attempts against one account", "brute_force"),
    ("credential guessing activity detected by security monitor", "brute_force"),
    ("login attempts failed repeatedly across user accounts", "brute_force"),
    ("repeated invalid credentials from same network address", "brute_force"),
    ("excessive authentication requests for a single user", "brute_force"),
    ("password spraying behavior against multiple accounts", "brute_force"),
    ("remote account access attempts repeatedly denied", "brute_force"),

    # Port scanning
    ("network scan detected many destination ports", "port_scan"),
    ("port scanning activity from remote host", "port_scan"),
    ("masscan detected against internal server", "port_scan"),
    ("suspicious connection attempts to many ports", "port_scan"),
    ("network reconnaissance port scan alert", "port_scan"),
    ("multiple ports probed by external address", "port_scan"),
    ("TCP SYN scan detected on network", "port_scan"),
    ("unusual sequential port connection attempts", "port_scan"),
    ("one host contacted numerous service ports", "port_scan"),
    ("repeated connection probes against remote services", "port_scan"),
    ("unexpected traffic across many destination endpoints", "port_scan"),
    ("remote host checking which network services respond", "port_scan"),
    ("series of short connections to different ports", "port_scan"),
    ("network mapping activity from unknown device", "port_scan"),
    ("many rejected connections to sequential TCP ports", "port_scan"),
    ("service discovery activity across several hosts", "port_scan"),
    ("unusual probing of available server ports", "port_scan"),
    ("multiple destination services tested by remote client", "port_scan"),

    # Malware
    ("malware detected on endpoint", "malware"),
    ("ransomware activity suspicious file encryption", "malware"),
    ("trojan detected by endpoint security", "malware"),
    ("virus detected quarantined malicious file", "malware"),
    ("malicious executable detected on workstation", "malware"),
    ("malware alert suspicious payload execution", "malware"),
    ("ransomware note found on host", "malware"),
    ("endpoint reports trojan infection", "malware"),
    ("unknown binary modified critical system files", "malware"),
    ("suspicious process attempted to download a payload", "malware"),
    ("endpoint security isolated infected executable", "malware"),
    ("unauthorized process encrypting user documents", "malware"),
    ("malicious file persistence detected on endpoint", "malware"),
    ("unexpected executable communicating with remote server", "malware"),
    ("security scanner identified infected application file", "malware"),
    ("possible spyware process found on workstation", "malware"),
    ("suspicious binary created files in system directory", "malware"),
    ("host protection blocked a malicious program", "malware"),

    # Privilege escalation
    ("privilege escalation detected on host", "privilege_escalation"),
    ("unauthorized privilege change detected", "privilege_escalation"),
    ("unexpected admin access by standard user", "privilege_escalation"),
    ("suspicious administrator privilege assignment", "privilege_escalation"),
    ("unauthorized root access attempt", "privilege_escalation"),
    ("user gained elevated privileges unexpectedly", "privilege_escalation"),
    ("privilege escalation security alert", "privilege_escalation"),
    ("unexpected elevation to administrator account", "privilege_escalation"),
    ("ordinary user obtained administrator permissions", "privilege_escalation"),
    ("process attempted to obtain elevated system rights", "privilege_escalation"),
    ("unexpected change to privileged account membership", "privilege_escalation"),
    ("unauthorized access to restricted administrative resource", "privilege_escalation"),
    ("standard account started process with elevated rights", "privilege_escalation"),
    ("unexpected root permission granted to application", "privilege_escalation"),
    ("privileged group membership changed without approval", "privilege_escalation"),
    ("service account acquired additional administrative access", "privilege_escalation"),
    ("restricted operation attempted with elevated permissions", "privilege_escalation"),
    ("unexpected administrator token assigned to process", "privilege_escalation"),

    # Suspicious scripts
    ("encoded powershell command detected", "suspicious_script"),
    ("suspicious powershell execution on endpoint", "suspicious_script"),
    ("malicious script execution detected", "suspicious_script"),
    ("obfuscated command launched by process", "suspicious_script"),
    ("encoded script downloaded and executed", "suspicious_script"),
    ("suspicious command line powershell activity", "suspicious_script"),
    ("obfuscated shell script detected", "suspicious_script"),
    ("unusual script interpreter execution", "suspicious_script"),
    ("script launched hidden command interpreter", "suspicious_script"),
    ("encoded command passed to system shell", "suspicious_script"),
    ("script attempted to disable endpoint protection", "suspicious_script"),
    ("unexpected scripting process spawned by office application", "suspicious_script"),
    ("unusual command interpreter activity on workstation", "suspicious_script"),
    ("obfuscated script attempted remote content retrieval", "suspicious_script"),
    ("script executed an encoded sequence of commands", "suspicious_script"),
    ("unexpected shell process started by background service", "suspicious_script"),
    ("suspicious automation script modified system settings", "suspicious_script"),
    ("script interpreter launched from temporary directory", "suspicious_script"),

    # Normal activity
    ("successful user login normal activity", "normal"),
    ("scheduled backup completed successfully", "normal"),
    ("routine system health check completed", "normal"),
    ("authorized administrator login successful", "normal"),
    ("normal application service started", "normal"),
    ("routine software update completed", "normal"),
    ("successful database connection by application", "normal"),
    ("standard user session ended normally", "normal"),
    ("approved software installed successfully", "normal"),
    ("scheduled maintenance completed without errors", "normal"),
    ("authorized user accessed permitted resource", "normal"),
    ("routine server heartbeat received", "normal"),
    ("normal application request completed successfully", "normal"),
    ("daily database backup verified successfully", "normal"),
    ("approved administrator changed application settings", "normal"),
    ("system monitoring check completed with healthy status", "normal"),
    ("authorized service account connected to database", "normal"),
    ("normal user logout recorded by operating system", "normal"),
]


def main():
    texts = [text for text, _ in DATA]
    labels = [label for _, label in DATA]

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )

    model = Pipeline([
        (
            "vectorizer",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=300,
                random_state=42,
                class_weight="balanced",
            ),
        ),
    ])

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print(f"Total examples: {len(DATA)}")
    print(f"Training examples: {len(X_train)}")
    print(f"Test examples: {len(X_test)}")
    print(f"Classes: {sorted(set(labels))}")
    print(f"Test accuracy: {accuracy_score(y_test, predictions):.2%}")
    print("\nClassification report:")
    print(classification_report(y_test, predictions, zero_division=0))

    model_path = (
        Path(__file__).resolve().parent
        / "models"
        / "threat_model.joblib"
    )
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    print(f"Model saved to: {model_path}")


if __name__ == "__main__":
    main()
