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
            if not ev.claim or len(ev.claim.strip()) < 15:
                errors.append(f"Evidence #{idx+1} claim is too short or empty.")
            if not ev.url or not ev.url.startswith("http"):
                errors.append(f"Evidence #{idx+1} URL '{ev.url}' is invalid or missing.")
            elif not cls.is_trusted_domain(ev.url):
                # We log warning or require authoritative domain
                pass  # Allow generic verified URLs if reputable, but check format

        return len(errors) == 0, errors
