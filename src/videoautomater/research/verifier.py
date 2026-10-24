"""Evidence verification gate for factual claims."""

from urllib.parse import urlparse

from videoautomater.models.research import FactualEvidence

# List of trusted source domains for science, space, history, and engineering
TRUSTED_SOURCE_DOMAINS = {
    "nasa.gov",
    "esa.int",
    "nature.com",
    "science.org",
    "sciencedirect.com",
    "arxiv.org",
    "nih.gov",
    "noaa.gov",
    "mit.edu",
    "stanford.edu",
    "ox.ac.uk",
    "cam.ac.uk",
    "britannica.com",
    "scientificamerican.com",
    "phys.org",
    "newscientist.com",
    "nationalgeographic.com",
    "si.edu",
    "usgs.gov",
    "cern.ch",
    "doi.org",
    "crossref.org",
    "cell.com",
    "pnas.org",
    "iaea.org",
}

import re

DOI_REGEX = re.compile(r"^https?://(dx\.)?doi\.org/10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$")
DISALLOWED_DOI_SUBSTRINGS = {"s41598-verified", "autonomous_investigation", "example", "placeholder", "fake"}
GENERIC_TEMPLATE_PHRASES = {
    "quantifiable structural anomalies",
    "non-linear physical interactions governing",
    "energy transfer efficiency previously considered unachievable",
}


class EvidenceVerifier:
    """Validates factual claims and source citations before topic approval."""

    @staticmethod
    def is_trusted_domain(url: str) -> bool:
        """Check if source URL belongs to an authoritative domain."""
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            if not netloc:
                return False
            for domain in TRUSTED_SOURCE_DOMAINS:
                if netloc == domain or netloc.endswith(f".{domain}"):
                    return True
            return False
        except (ValueError, AttributeError):
            return False

    @classmethod
    def verify_evidence(cls, evidence_list: list[FactualEvidence]) -> tuple[bool, list[str]]:
        """Verify list of evidence citations.

        Returns:
            (passed, list_of_failure_reasons)
        """
        if not evidence_list:
            return False, ["Evidence list is empty. Topics must contain at least one verifiable source citation."]

        errors = []
        for idx, ev in enumerate(evidence_list):
            claim_text = (ev.claim or "").strip()
            if len(claim_text) < 20:
                errors.append(f"Evidence #{idx+1} claim is too short or empty (min 20 characters required).")
            elif any(phrase in claim_text for phrase in GENERIC_TEMPLATE_PHRASES):
                errors.append(f"Evidence #{idx+1} contains generic fabricated template phrasing.")

            if not ev.url or not ev.url.startswith("http"):
                errors.append(f"Evidence #{idx+1} URL '{ev.url}' is invalid or missing.")
            else:
                # Check for DOI validity if URL is a DOI
                if "doi.org" in ev.url:
                    if not DOI_REGEX.match(ev.url):
                        errors.append(f"Evidence #{idx+1} DOI URL '{ev.url}' does not conform to valid DOI syntax.")
                    if any(bad in ev.url.lower() for bad in DISALLOWED_DOI_SUBSTRINGS):
                        errors.append(f"Evidence #{idx+1} contains placeholder or fabricated DOI: '{ev.url}'.")
                elif not cls.is_trusted_domain(ev.url):
                    errors.append(f"Evidence #{idx+1} URL domain is untrusted: '{ev.url}'.")

                # Preprint validation: distinguish preprints from peer-reviewed articles
                is_preprint = (
                    not getattr(ev, "is_peer_reviewed", True)
                    or getattr(ev, "publication_type", "") == "PREPRINT"
                    or any(pre in ev.url.lower() for pre in ["10.20944", "arxiv.org", "biorxiv.org", "preprints.org", "researchsquare.com"])
                )
                if is_preprint:
                    if ev.verified:
                        errors.append(f"Evidence #{idx+1} cannot be marked verified: cited source '{ev.url}' is an unreviewed preprint.")
                    if any(term in claim_text.lower() for term in ["peer-reviewed", "peer reviewed", "refereed journal"]):
                        errors.append(f"Evidence #{idx+1} claim falsely asserts peer-reviewed status for an unreviewed preprint.")

                # Ensure source actually supports the claim
                if ev.verified and (len(claim_text) < 25 or any(bad in claim_text.lower() for bad in ["unconfirmed internal", "unsupported hypothesis", "pseudoscientific"])):
                    errors.append(f"Evidence #{idx+1} cannot be marked verified: claim lacks substantiated peer-reviewed evidence.")

        return len(errors) == 0, errors
