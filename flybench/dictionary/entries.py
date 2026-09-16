"""Conservative selectors for the Phase 2 annotation snapshots.

Type matching is case-sensitive and anchored. A functional name does not
establish a genetic identity or imply a sex-shared behavioural function.
"""

from dataclasses import asdict, dataclass
import re

from flybench.graph.select import where

DATASETS = ("male", "female", "banc")
SOURCES = {
    "atlas": ("Schlegel et al. (2024), whole-brain cell typing", "https://doi.org/10.1038/s41586-024-07686-5"),
    "male": ("MaleCNS v1.0 official body annotations", "https://male-cns.janelia.org/download/"),
    "banc": ("BANC, distributed brain-and-cord control circuits", "https://doi.org/10.1038/s41586-026-10735-w"),
    "jo": ("Auditory responses of Johnston's organ neurons (2013)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3734059/"),
    "orn": ("Systematic morphology of identified ORNs (2021)", "https://elifesciences.org/articles/69896"),
    "contact": ("Thistle et al. (2012), contact chemoreceptors", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3365544/"),
    "ppk25": ("Vijayan et al. (2014), ppk25 pheromone neurons", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3967927/"),
    "visual": ("Matsliah et al. (2024), visual-system parts list", "https://doi.org/10.1038/s41586-024-07981-1"),
    "lc10": ("Sten et al. (2021), arousal gates visual processing", "https://doi.org/10.1038/s41586-021-03714-w"),
    "p1": ("Hoopfer et al. (2015), P1 and persistent social state", "https://elifesciences.org/articles/11346"),
    "pc1": ("Deutsch et al. (2020), persistent female internal state", "https://elifesciences.org/articles/59502"),
    "song": ("von Philipsborn et al. (2011), control of courtship song", "https://doi.org/10.1016/j.neuron.2011.01.011"),
    "nested": ("Lillvis et al. (2024), nested song circuits", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/"),
    "vpo": ("Wang et al. (2021), female sexual receptivity circuits", "https://doi.org/10.1038/s41586-020-2972-7"),
    "dn": ("Marin et al. (2025), descending/ascending comparison", "https://doi.org/10.1038/s41586-025-08925-z"),
    "social": ("Social state alters vision (2024)", "https://doi.org/10.1038/s41586-024-08255-6"),
    "mate": ("Clowney et al. (2015), excitation/inhibition and mate choice", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4695383/"),
    "mb": ("Li et al. (2020), mushroom-body connectome", "https://elifesciences.org/articles/62576"),
    "apl": ("Amin et al. (2020), localized mushroom-body inhibition", "https://elifesciences.org/articles/56954"),
    "oa": ("Octopaminergic descending neurons (2024)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11064449/"),
}


@dataclass(frozen=True)
class Selector:
    type_re: str = r"^.*$"
    side: str | None = None
    superclass: str | None = None
    nt: str | None = None
    cell_class: str | None = None

    def select(self, graph):
        indices = where(graph, type_re=self.type_re, side=self.side,
                        superclass=self.superclass)
        # graph.select has no NT/class predicates. These exact postfilters
        # preserve its AND semantics and fail closed on missing columns.
        for column, value in (("nt", self.nt), ("class", self.cell_class)):
            if value is not None:
                indices = indices[graph[column][indices] == value]
        return indices


@dataclass(frozen=True)
class Entry:
    name: str
    dataset: str
    selector: Selector
    role: str
    literature: str
    confidence: str
    notes: str
    source: str
    evidence_class: str = ""
    read_only: bool = False

    def to_dict(self):
        return asdict(self)


# Verified against body-annotations.fruDsx
# and dimorphism: coexpress_high AND male-specific; ambiguous 2a/2b excluded.
P1_TYPES = ("pC1_1a", "pC1_1b", "pC1_2a", "pC1_2b", "pC1_2c",
            "pC1_3a", "pC1_3b", "pC1_3c", "pC1_5b", "pC1_6b",
            "pC1_15a", "pC1_16a", "pC1_16b")
MALE_WING_TYPES = ("DLMn a, b", "DLMn c-f", "DVMn 1a-c", "DVMn 2a, b",
                   "DVMn 3a, b", "b1 MN", "b2 MN", "b3 MN", "i1 MN",
                   "i2 MN", "iii1 MN", "iii3 MN", "ps1 MN", "ps2 MN",
                   "tp1 MN", "tp2 MN", "tpn MN")
ORN_GLOMERULI = (
    "D DA1 DA2 DA3 DA4l DA4m DC1 DC2 DC3 DC4 DL1 DL2d DL2v DL3 DL4 DL5 "
    "DM1 DM2 DM3 DM4 DM5 DM6 DP1l DP1m V VA1d VA1v VA2 VA3 VA4 VA5 VA6 "
    "VA7l VA7m VC1 VC2 VC3 VC4 VC5 VL1 VL2a VL2p VM1 VM2 VM3 VM4 VM5d "
    "VM5v VM6 VM6l VM6m VM6v VM7d VM7v"
).split()


def literals(names):
    return "^(?:" + "|".join(re.escape(n) for n in names) + ")$"


@dataclass(frozen=True)
class VpoENInputEntry(Entry):
    """Anatomical diagnostic group; existing Entry serialization is unchanged."""

    group: str = "vpoen-input"


VPOEN_INPUT_TYPES = (
    "CB1484", "CB2364", "CB1383", "WED104", "AN_AVLP_8",
    "CB2633", "PVLP021", "CB1869", "CB2449", "CB1614",
)


def entries(dataset):
    """Return new immutable definitions; counts are measured by build.audit."""
    if dataset not in DATASETS:
        raise ValueError(f"dataset must be one of {DATASETS}, got {dataset!r}")
    result = []

    def add(name, pattern, role, source, claim, confidence="exact", notes="", **filters):
        title, url = SOURCES[source]
        result.append(Entry(name, dataset, Selector(pattern, **filters), role,
                            f"{title}: {claim}.", confidence, notes, url))

    for name in ("JO-A", "JO-B"):
        add(name, rf"^{name}(?:[1-4](?:_[abc])?)?$", "sensory_input", "jo",
            "A/B Johnston's-organ populations respond to sound", "family",
            "Numbered subtypes included; '-unclear', JO-mz and other JO families excluded.")
    add("ORN", r"^ORN(?:_[A-Za-z0-9]+)?$", "sensory_input", "orn",
        "olfactory receptor neurons project to named glomeruli", "family",
        "ORN annotation family includes non-Or receptor classes; it is not proof of Or expression. D_ORN is excluded.")
    add("Or*", r"^Or[0-9]+[a-z]+$", "sensory_input", "orn",
        "receptor genes identify olfactory sensory classes", "family",
        "Literal receptor-labelled types only; no gene identity inferred from arbitrary ORN names.")
    for name, glomerulus in (("Or47b", "VA1v"), ("Or67d", "DA1")):
        add(name, rf"^ORN_{glomerulus}$", "sensory_input", "orn",
            f"{name} ORNs innervate {glomerulus}", "proxy",
            "Glomerular type proxy; receptor expression is not measured in the graph.")
    for name in ("Gr32a", "ppk23", "ppk25"):
        add(name, rf"^{name}$", "sensory_input", "ppk25" if name == "ppk25" else "contact",
            "contact chemosensory pathways contribute to mate recognition",
            notes="Literal gene-labelled type only; unnamed gustatory neurons are not substituted.")
    for name in ("L1", "L2"):
        add(name, rf"^{name}$", "sensory_input", "visual", "lamina neurons relay early visual input")
    add("R1-R6", r"^R1-(?:R)?6$", "sensory_input", "visual",
        "outer photoreceptors provide visual input", "family",
        "Matches the two observed aggregate spellings R1-R6 and R1-6; no generic R prefix.")
    for name in ("LC10a", "LC10b", "LC10c", "LC10d"):
        add(name, rf"^{name}(?:-[12])?$" if name == "LC10c" else rf"^{name}$",
            "readout", "lc10" if name == "LC10a" else "visual",
            "LC10a participates in visual pursuit" if name == "LC10a" else "LC types are visual projection neurons",
            "family" if name == "LC10c" else "exact",
            "LC10c-1/-2 are pooled; unclassified LC10 is excluded." if name == "LC10c" else "")
    for name in ("AOTU019", "AOTU025"):
        add(name, rf"^{name}$", "readout", "atlas", "atlas identifies anterior optic tubercle cell types",
            notes="Anatomical readout; no specific courtship function is asserted.")
    add("P1", literals(P1_TYPES) if dataset == "male" else r"^P1(?:_[0-9]+[a-z]?)?$",
        "state", "p1", "P1 activation promotes persistent social arousal", "proxy",
        "MaleCNS v1.0 has pC1 rather than P1 types. Frozen conservative proxy: coexpress_high and male-specific official annotations; coexpress_low, potentially male-specific, dsx-only, pC1x and ambiguous pC1_2a/2b excluded. Not a P1a driver match. Female P1-9 is unrelated and excluded.",
        superclass="cb_intrinsic" if dataset == "male" else None)
    for suffix in "abcde":
        name = "pC1" + suffix
        add(name, rf"^{name}$", "state", "pc1", "female pC1 subtypes participate in social state circuits",
            notes="Subtype identity only; pC1d/e persistent-state evidence is not generalized to every subtype.")
    for name in ("pIP10", "vPR6", "vMS11", "pMP2", "dPR1", "TN1A"):
        pattern = r"^TN1a(?:_[a-i])?$" if name == "TN1A" else rf"^{name}$"
        add(name, pattern, "readout", "nested" if name in ("pMP2", "dPR1", "TN1A") else "song",
            "identified descending/VNC circuits participate in male song",
            "family" if name == "TN1A" else "exact",
            "TN1a subtypes pooled; TN1c excluded. Female homologues do not establish male song function." if name == "TN1A" else
            "Functional evidence is from males; matching a female type does not establish song production.")
    add("vpoDN", r"^(?:DNp37|vpoDN)$", "readout", "dn", "vpoDN (DNp37) controls female vaginal plate opening")
    for name in ("vpoEN", "vpoIN"):
        # Legacy vpoIN selector: ^vpoIN$
        # 0 cells in FAFB v783 and BANC v888; renamed 2026-09-16
        add(name, r"^CB1385$" if name == "vpoIN" and dataset != "male" else rf"^{name}$", "state", "vpo", "excitatory/inhibitory song pathways regulate female receptivity",
            notes="Sex-shared label is not evidence of a shared behavioural output.")
    sag = {"male": r"^SAG$", "female": r"^(?:SAG|SpsP)$", "banc": r"^ANXXX983$"}[dataset]
    add("SAG", sag, "state", "banc", "ANXXX983/SAG carries reproductive-tract state toward pC1",
        "proxy" if dataset == "female" else "exact",
        "FAFB SpsP is a requested candidate proxy, not a verified cell-for-cell SAG identity; IbSpsP excluded." if dataset == "female" else
        "BANC ANXXX983 alias is supported by the BANC paper; male SpsP is not assumed homologous.")
    add("oviDN", r"^oviDN(?:[ab](?:_[ab])?)?$", "readout", "dn", "oviDN pathways participate in oviposition", "family")
    add("DNp13/pMN1", r"^(?:DNp13|pMN1)$", "readout", "dn",
        "DNp13/pMN1 drives female ovipositor extrusion and has sex-specific VNC targets")
    add("pCd", r"^pCd(?:[0-9]+[a-z]?)?$", "state", "pc1", "persistent courtship state involves pCd",
        "family", "No synonym inferred from an unrelated anatomical label.")
    add("aIPg", r"^aIPg(?:[0-9]+|_m[1-4])?$", "state", "social", "aIPg links female aggression and visual processing",
        "family", "Only explicit aIPg types; functional identity of male subtypes is not established.")
    add("mAL", r"^mAL(?:[0-9]+[A-I]?[0-9]?|[BCD][1-6]|_[mf][0-9]+[abc]?)?$",
        "state", "mate", "mAL inhibition contributes to mate choice", "family",
        "Anatomical type family is broader than the functional mAL driver population.")
    add("vAB3", r"^vAB3$", "state", "mate", "ascending pheromone pathways excite courtship circuitry")
    for name in ("DNa01", "DNa02", "DNp09", "MDN", "DNg100", "DNb08"):
        add(name, rf"^{name}$", "readout", "banc", "descending pathways provide locomotor-related readouts",
            notes="Readout designation does not imply a pure walking command or motor-neuron identity.")
    wing_pattern = literals(MALE_WING_TYPES) if dataset == "male" else r"^.*$"
    add("wing_motor", wing_pattern, "motor", "dn", "wing motor neurons are targets of descending/VNC circuits",
        "proxy" if dataset == "male" else "family",
        "Male graph lacks a wing-motor class: finite named steering/power subset, not a complete wing MN census." if dataset == "male" else
        "Exact class filter; FAFB brain-only graph may have no wing motor population.",
        superclass="vnc_motor" if dataset == "male" else "motor",
        cell_class=None if dataset == "male" else "wing_motor_neuron")
    for name in ("ps1", "i1", "iii1", "b3"):
        pattern = r"^(?:ps1 MN|PS1)$" if name == "ps1" else rf"^{name}(?: MN)?$"
        add(name + "_MN", pattern, "motor", "nested", "named wing motor neurons participate in wing control",
            superclass="vnc_motor" if dataset == "male" else "motor",
            notes="BANC PS1 spelling is constrained to motor superclass; no case-insensitive PS100 match.")
    for name, pattern in (("PAM", r"^PAM(?:[0-9]{2})?$"), ("PPL1", r"^PPL1(?:[0-9]{2})?$")):
        add(name, pattern, "modulatory", "mb", "dopaminergic mushroom-body inputs support reinforcement learning",
            "family", "Type family membership; the observed NT distribution is reported, not overwritten.")
    add("serotonin", r"^.*$", "modulatory", "atlas", "source NT annotations identify serotonergic candidates",
        "proxy", "NT prediction only; no confidence threshold or serotonergic gene/driver verification.", nt="serotonin")
    add("octopamine", r"^.*$", "modulatory", "oa", "octopaminergic neurons modulate locomotor and other circuits",
        "proxy", "NT-labelled octopamine only. Tdc2 also labels tyraminergic neurons, so this is not the full Tdc2 population.", nt="octopamine")
    add("KC", r"^KC(?:ab(?:-(?:ap1|[cmps]))?|a'b'(?:-(?:ap[12]|m))?|apbp-(?:ap[12]|m)|g(?:-(?:[dm]|s[1-4]))?)?$",
        "state", "mb", "Kenyon cells provide mushroom-body representations for learning", "family")
    add("MBON", r"^MBON[0-9]{2}$", "readout", "mb", "mushroom-body output neurons carry learned output",
        "family", "Ambiguous comma-joined types and '-like' cells excluded, including BANC MBON25,MBON34.")
    add("APL", r"^APL$", "modulatory", "apl", "APL provides feedback inhibition to Kenyon cells")
    for glomerulus in ORN_GLOMERULI:
        name = "ORN_" + glomerulus
        add(name, rf"^{name}$", "sensory_input", "orn", "glomerular labels distinguish olfactory input classes",
            notes="Glomerular class, not a receptor-expression measurement; overlaps ORN and possibly receptor proxies.")
    # E3 report mappings are hypotheses, not verified driver identities.
    # Literature links provide context; the supplied external report itself
    # has no supplied bibliographic identifier or independently checked roots.
    def add_e3(name, pattern, evidence, notes, read_only=False):
        title, url = SOURCES["atlas"]
        result.append(Entry(
            name, dataset, Selector(pattern), "readout", title, "proxy",
            notes + " Literature link is atlas context, not crosswalk provenance.",
            url, evidence, read_only))

    crosswalk = "annotation crosswalk, external report, REPORTED"
    connectivity = "graph connectivity, lane k2"
    add_e3("AMMC-B1-candidate", r"^(?:CB1078|CB1542|SAD053)$", crosswalk,
           "Primary candidate from the task-supplied external annotation report: "
           "aPN1/AMMC-B1 maps to CB1078/CB1542 with additional SAD053 members. "
           "Annotation membership takes priority over connectivity ranking; "
           "do not merge with AMMC-B1-candidate-graph.")
    add_e3("AMMC-B1-candidate-graph", r"^(?:CB1076|CB1125|CB2789)$", connectivity,
           "Secondary sensitivity population from lane k2 connectivity discovery; "
           "not an annotation synonym for the primary AMMC-B1 candidate.")
    add_e3("A2-candidate", r"^CB1817[ab]$", connectivity,
           "Modern AMMC-A2 identity is UNRESOLVED. Read-only diagnostic population; "
           "not a drive or hook target.", read_only=True)
    add_e3("vpoDN-GABA-input", r"^AVLP008$", connectivity,
           "Task-supplied graph report: GABAergic input to DNp37 and pC1. "
           "Connectivity signature is distinct from the reported vpoIN alias CB1385.")
    add_e3("aLN-m", {"female": r"^CB3880$", "banc": r"^CB3880$",
                     "male": r"^WED191$"}[dataset], crosswalk,
           "Task-supplied external report: female CB3880 corresponds to male WED191 "
           "(aLN(m)); BANC uses the female type spelling. Matching labels and "
           "GABA annotations do not establish cell-for-cell homology.")
    # Keep the established vpoIN role/source while recording E3 provenance.
    from dataclasses import replace
    result = [replace(entry, evidence_class=crosswalk,
                      notes=entry.notes + " Task-supplied external report maps vpoIN "
                      "to CB1385 in female/BANC; legacy ^vpoIN$: 0 cells in FAFB v783 and BANC v888; "
                      "renamed 2026-09-16. MaleCNS retains ^vpoIN$ (five cells). "
                      "AVLP008 is a separate connectivity population.")
              if entry.name == "vpoIN" else entry for entry in result]
    # The rank is from FAFB v783; literal labels in other graphs are not aliases.
    for name, pattern in (
        *(("vpoEN-input:" + cell_type, literals((cell_type,)))
          for cell_type in VPOEN_INPUT_TYPES),
        ("vpoEN-input-top10", literals(VPOEN_INPUT_TYPES)),
    ):
        result.append(VpoENInputEntry(
            name, dataset, Selector(pattern), "readout",
            SOURCES["atlas"][0] + ": annotation context only; rank evidence is vpoen_inputs_v1.",
            "exact",
            "anatomical input rank in vpoen_inputs_v1; not a drive target; function unknown",
            SOURCES["atlas"][1], "records/vpoen_inputs_v1_report.md", True))
    return tuple(result)
