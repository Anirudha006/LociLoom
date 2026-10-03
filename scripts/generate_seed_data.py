"""
LociLoom Seed Data Generator
Generates:
1. data/concept_visual_dictionary.json (>200 curated concept-to-object mappings)
2. data/concepts_seed.csv (>300 labeled concepts for topic & difficulty classification)
3. data/recall_logs_seed.csv (>2000 simulated study & recall logs for forgetting model)
"""
import os
import json
import random
import csv
import math

SEED = 42
random.seed(SEED)

def generate_curated_dictionary():
    dictionary = {
        # Biology (45 entries)
        "photosynthesis": {"emoji": "🌱", "object": "Solar-powered emerald plant", "topic": "Biology", "reason": "Plants absorbing radiant sunlight to make nourishment"},
        "sunlight": {"emoji": "🕶️", "object": "Neon glowing sunglasses", "topic": "Biology", "reason": "Direct radiant light driving the solar reaction"},
        "water": {"emoji": "💧", "object": "Crystalline water bottle", "topic": "Biology", "reason": "Essential fluid absorbed by root xylem"},
        "carbon dioxide": {"emoji": "🎈", "object": "Heavy grey gas balloon", "topic": "Biology", "reason": "Floating ambient gas taken in through open stomata"},
        "glucose": {"emoji": "🍬", "object": "Glistening sugar cubes", "topic": "Biology", "reason": "Sweet energy-rich hexose fuel created by the plant"},
        "oxygen": {"emoji": "🫧", "object": "Sparkling transparent bubbles", "topic": "Biology", "reason": "Fresh revitalizing byproduct released into the atmosphere"},
        "chloroplast": {"emoji": "🍳", "object": "Green frying pan with solar cells", "topic": "Biology", "reason": "Organelle kitchen where photosynthetic food is cooked"},
        "chlorophyll": {"emoji": "🎨", "object": "Vibrant green paint bucket", "topic": "Biology", "reason": "Pigment dyeing the leaves green and capturing photon energy"},
        "mitochondria": {"emoji": "🔋", "object": "Humming electric generator battery", "topic": "Biology", "reason": "The quintessential powerhouse producing cellular ATP"},
        "atp": {"emoji": "⚡", "object": "Zapping lightning canister", "topic": "Biology", "reason": "Universal biochemical energy currency for cellular work"},
        "dna": {"emoji": "🧬", "object": "Twisted spiral staircase of jewels", "topic": "Biology", "reason": "Double helix blueprint coding biological life"},
        "rna": {"emoji": "📜", "object": "Single scroll of parchment", "topic": "Biology", "reason": "Single-stranded messenger delivering genetic blueprints"},
        "ribosome": {"emoji": "🏭", "object": "Miniature protein assembly factory", "topic": "Biology", "reason": "Cellular machinery translating mRNA into peptide chains"},
        "nucleus": {"emoji": "🏛️", "object": "Marble fortress control tower", "topic": "Biology", "reason": "Command center enclosing and safeguarding chromatin"},
        "membrane": {"emoji": "🛡️", "object": "Gated perimeter security shield", "topic": "Biology", "reason": "Selective lipid barrier controlling transport in and out"},
        "enzyme": {"emoji": "✂️", "object": "Golden catalytic scissors", "topic": "Biology", "reason": "Biological catalysts speeding up metabolic reactions"},
        "osmosis": {"emoji": "🧽", "object": "Porous soaking sponge", "topic": "Biology", "reason": "Passive solvent diffusion across semipermeable membranes"},
        "mitosis": {"emoji": "👥", "object": "Identical twin puppets dividing", "topic": "Biology", "reason": "Cell replication producing two diploid clones"},
        "meiosis": {"emoji": "🎲", "object": "Four-sided shuffling dice", "topic": "Biology", "reason": "Gamete division creating four unique haploid daughter cells"},
        "neuron": {"emoji": "💡", "object": "Branching fiber-optic tree lamp", "topic": "Biology", "reason": "Electrically excitable cells transmitting signal pulses"},
        "synapse": {"emoji": "🌉", "object": "Sparking suspension footbridge", "topic": "Biology", "reason": "Microscopic junction where neurotransmitters leap"},
        "hemoglobin": {"emoji": "🛞", "object": "Red wheelbarrow holding oxygen tanks", "topic": "Biology", "reason": "Iron-rich carrier protein transporting oxygen in blood"},
        "ecosystem": {"emoji": "🌐", "object": "Living glass biosphere terrarium", "topic": "Biology", "reason": "Interconnected community of organisms and environment"},
        "mutation": {"emoji": "🔀", "object": "Mismatched kaleidoscope", "topic": "Biology", "reason": "Unscheduled nucleotide alteration in genetic sequence"},
        "homeostasis": {"emoji": "⚖️", "object": "Self-leveling brass balance scale", "topic": "Biology", "reason": "Dynamic physiological equilibrium keeping systems steady"},
        "antibody": {"emoji": "🏹", "object": "Y-shaped defensive golden arrows", "topic": "Biology", "reason": "Immune proteins tagging foreign antigen invaders"},
        "antigen": {"emoji": "🎯", "object": "Fluorescent foreign target flag", "topic": "Biology", "reason": "Molecular surface marker triggering immune detection"},
        "xylem": {"emoji": "🪵", "object": "Vertical bamboo straw pipe", "topic": "Biology", "reason": "Vascular tissue pulling water upward from roots"},
        "phloem": {"emoji": "🍯", "object": "Sticky honey slide tube", "topic": "Biology", "reason": "Vascular tissue transporting sugars downward and throughout"},
        "stomata": {"emoji": "👄", "object": "Tiny opening breathing lips on a leaf", "topic": "Biology", "reason": "Microscopic pores regulating leaf gas exchange"},
        "transpiration": {"emoji": "💨", "object": "Steaming teakettle leaf", "topic": "Biology", "reason": "Water evaporation pulling xylem column skyward"},
        "fermentation": {"emoji": "🍺", "object": "Bubbling copper yeast vat", "topic": "Biology", "reason": "Anaerobic sugar breakdown producing ethanol or lactate"},
        "glycolysis": {"emoji": "🪓", "object": "Sharp axe splitting a glucose crystal", "topic": "Biology", "reason": "Ten-step enzymatic cleavage of hexose into pyruvate"},
        "krebs cycle": {"emoji": "🎡", "object": "Ferris wheel churning carbon atoms", "topic": "Biology", "reason": "Cyclic mitochondrial cascade generating NADH and FADH2"},
        "endoplasmic reticulum": {"emoji": "🛣️", "object": "Folded labyrinth highway ribbon", "topic": "Biology", "reason": "Folded network synthesizing lipids and modifying proteins"},
        "golgi apparatus": {"emoji": "📦", "object": "Automated postal sorting conveyer", "topic": "Biology", "reason": "Packaging and addressing vesicles for secretion"},
        "lysosome": {"emoji": "🗑️", "object": "Acidic recycling disposal bin", "topic": "Biology", "reason": "Enzyme-filled sac digesting cellular waste and debris"},
        "vacuole": {"emoji": "🛟", "object": "Massive pressurized water reservoir", "topic": "Biology", "reason": "Central plant storage chamber maintaining turgor"},
        "hormone": {"emoji": "✉️", "object": "Sealed royal courier dispatch letter", "topic": "Biology", "reason": "Circulating chemical messenger signaling distant tissues"},
        "cytoplasm": {"emoji": "🍮", "object": "Translucent jelly cushion", "topic": "Biology", "reason": "Gelatinous fluid suspending cellular organelles"},
        "chromosome": {"emoji": "🧶", "object": "Tightly wound spool of wool", "topic": "Biology", "reason": "Condensed chromatin packaging genetic DNA"},
        "allele": {"emoji": "🏷️", "object": "Alternative color tags on a coat", "topic": "Biology", "reason": "Different variant forms of the same gene locus"},
        "phenotype": {"emoji": "🪞", "object": "Looking-glass displaying exterior appearance", "topic": "Biology", "reason": "Observable physical trait expressed by genetic code"},
        "genotype": {"emoji": "🧾", "object": "Secret folded blueprint receipt", "topic": "Biology", "reason": "Internal genetic makeup underlying physical traits"},
        "natural selection": {"emoji": "🏹", "object": "Weathering sieve selecting sturdy stones", "topic": "Biology", "reason": "Evolutionary survival of best-adapted phenotypic variants"},

        # Physics (40 entries)
        "gravity": {"emoji": "🍎", "object": "Falling crimson apple", "topic": "Physics", "reason": "Newtonian universal attraction pulling mass toward center"},
        "friction": {"emoji": "🛹", "object": "Coarse sandpaper skating ramp", "topic": "Physics", "reason": "Resistive force opposing relative sliding motion"},
        "inertia": {"emoji": "🪨", "object": "Heavy immovable granite boulder", "topic": "Physics", "reason": "Property of mass resisting any change in velocity"},
        "acceleration": {"emoji": "🏎️", "object": "Roaring rocket sports car", "topic": "Physics", "reason": "Rate of change of velocity over elapsed time"},
        "velocity": {"emoji": "🏹", "object": "Speeding directional arrow", "topic": "Physics", "reason": "Vector speed combined with precise direction of travel"},
        "momentum": {"emoji": "🎳", "object": "Heavy rolling bowling ball knocking pins", "topic": "Physics", "reason": "Product of mass and velocity driving through impacts"},
        "kinetic energy": {"emoji": "🎢", "object": "Zooming downhill roller coaster", "topic": "Physics", "reason": "Mechanical energy possessed due to motion"},
        "potential energy": {"emoji": "🏹", "object": "Fully drawn taut wooden bowstring", "topic": "Physics", "reason": "Stored energy due to elevated position or strain"},
        "thermodynamics": {"emoji": "🔥", "object": "Blazing iron furnace engine", "topic": "Physics", "reason": "Laws governing heat, work, and entropy conversion"},
        "entropy": {"emoji": "💥", "object": "Shattering porcelain teacup", "topic": "Physics", "reason": "Tendency toward cosmic disorder and unavailable energy"},
        "quantum": {"emoji": "🎲", "object": "Spinning probability dice cube", "topic": "Physics", "reason": "Discrete packet of energy governed by wave mechanics"},
        "photon": {"emoji": "🔦", "object": "Beaming golden laser flashlight", "topic": "Physics", "reason": "Massless elementary quantum particle of light"},
        "electromagnetism": {"emoji": "🧲", "object": "Horseshoe magnet sparking blue arcs", "topic": "Physics", "reason": "Coupled fundamental force of electricity and magnetism"},
        "refraction": {"emoji": "📐", "object": "Prismatic triangular glass prism", "topic": "Physics", "reason": "Bending of wave velocity across differing media"},
        "reflection": {"emoji": "🪞", "object": "Polished silver mirror bounce", "topic": "Physics", "reason": "Wavefront bouncing back from an interface boundary"},
        "diffraction": {"emoji": "🌊", "object": "Ocean waves spreading past a narrow pier", "topic": "Physics", "reason": "Wave bending and spreading around obstacles or slits"},
        "resonance": {"emoji": "🔔", "object": "Humming bronze tuning fork", "topic": "Physics", "reason": "Dramatic amplitude surge at natural harmonic frequency"},
        "superconductivity": {"emoji": "🧊", "object": "Levitating frosty frozen puck", "topic": "Physics", "reason": "Zero electrical resistance at cryogenic temperatures"},
        "relativity": {"emoji": "🕰️", "object": "Melting warped grandfather clock", "topic": "Physics", "reason": "Einsteinian spacetime dilation relative to observer speed"},
        "black hole": {"emoji": "🕳️", "object": "Swirling pitch-black cosmic whirlpool", "topic": "Physics", "reason": "Singularity whose gravitational escape velocity exceeds light"},
        "centripetal force": {"emoji": "🎡", "object": "Swinging tetherball on a tight string", "topic": "Physics", "reason": "Center-directed force keeping an object in curved orbit"},
        "torque": {"emoji": "🔧", "object": "Long chrome wrench turning a bolt", "topic": "Physics", "reason": "Rotational mechanical force producing angular acceleration"},
        "buoyancy": {"emoji": "🦆", "object": "Floating yellow rubber duck", "topic": "Physics", "reason": "Upward hydrostatic force exerted by displaced fluid"},
        "archimedes principle": {"emoji": "🛁", "object": "Overflowing marble bathtub", "topic": "Physics", "reason": "Displaced liquid volume equaling immersed body weight"},
        "bernoulli principle": {"emoji": "✈️", "object": "Curved airplane wing in wind tunnel", "topic": "Physics", "reason": "Higher fluid velocity corresponding to lower pressure"},
        "doppler effect": {"emoji": "🚑", "object": "Screeching siren ambulance zooming past", "topic": "Physics", "reason": "Frequency shift caused by relative motion of source"},
        "coulombs law": {"emoji": "⚡", "object": "Two clinging static balloons", "topic": "Physics", "reason": "Electrostatic attraction and repulsion between charges"},
        "magnetic field": {"emoji": "🧭", "object": "Twitching brass compass needle", "topic": "Physics", "reason": "Vector field exerting force on moving magnetic poles"},
        "capacitance": {"emoji": "🪫", "object": "Parallel metal plates holding electric charge", "topic": "Physics", "reason": "Ability of a system to store electrostatic charge"},
        "inductance": {"emoji": "🌀", "object": "Coiled copper solenoid spring", "topic": "Physics", "reason": "Tendency of electrical conductor to oppose current shifts"},
        "newtons first law": {"emoji": "🪨", "object": "Resting rock that refuses to move", "topic": "Physics", "reason": "Law of inertia: velocity remains constant unless acted upon"},
        "newtons second law": {"emoji": "🏋️", "object": "Barbell accelerating under strong push (F=ma)", "topic": "Physics", "reason": "Force equals mass multiplied by acceleration"},
        "newtons third law": {"emoji": "🚀", "object": "Rocket shooting gas down to launch upward", "topic": "Physics", "reason": "For every action there is an equal and opposite reaction"},
        "wave-particle duality": {"emoji": "🎭", "object": "Two-faced mask showing wave and pebble", "topic": "Physics", "reason": "Quantum entities exhibiting both wave and particle nature"},
        "special relativity": {"emoji": "🚄", "object": "Bullet train approaching speed of light", "topic": "Physics", "reason": "Constancy of light speed causing time dilation and length contraction"},
        "general relativity": {"emoji": "🕸️", "object": "Bowling ball warping a rubber trampoline sheet", "topic": "Physics", "reason": "Gravity explained as curvature of spacetime continuum"},
        "radiation": {"emoji": "☢️", "object": "Glowing emerald uranium glass bead", "topic": "Physics", "reason": "Emission of energetic particles or electromagnetic waves"},
        "half-life": {"emoji": "⏳", "object": "Hourglass with radioactive sand falling", "topic": "Physics", "reason": "Time required for half of radioactive nuclei to decay"},
        "nuclear fission": {"emoji": "💥", "object": "Heavy uranium melon splitting into two", "topic": "Physics", "reason": "Heavy atomic nucleus dividing and releasing massive energy"},
        "nuclear fusion": {"emoji": "☀️", "object": "Blazing core of the noon sun", "topic": "Physics", "reason": "Light hydrogen nuclei fusing under pressure into helium"},

        # Chemistry (35 entries)
        "atom": {"emoji": "⚛️", "object": "Solar system model with orbiting metal spheres", "topic": "Chemistry", "reason": "Fundamental building block of matter with nucleus and electrons"},
        "electron": {"emoji": "🐝", "object": "Buzzing neon bumblebee orbiting a hive", "topic": "Chemistry", "reason": "Negatively charged subatomic particle in electron cloud"},
        "proton": {"emoji": "🔴", "object": "Positive ruby core sphere", "topic": "Chemistry", "reason": "Positively charged nucleon defining atomic number"},
        "neutron": {"emoji": "⚪", "object": "Neutral silver weight in the nucleus", "topic": "Chemistry", "reason": "Uncharged subatomic particle stabilizing atomic nucleus"},
        "covalent bond": {"emoji": "🤝", "object": "Two hands firmly clasped sharing rings", "topic": "Chemistry", "reason": "Chemical bond formed by mutual sharing of electron pairs"},
        "ionic bond": {"emoji": "🎁", "object": "Delivering a gift package from donor to receiver", "topic": "Chemistry", "reason": "Electrostatic bond formed by complete electron transfer"},
        "hydrogen bond": {"emoji": "🧲", "object": "Velcro tape strip connecting water droplets", "topic": "Chemistry", "reason": "Weak dipole-dipole attraction between electronegative atoms"},
        "ph": {"emoji": "🧪", "object": "Color-shifting rainbow litmus paper strip", "topic": "Chemistry", "reason": "Logarithmic measure of hydrogen ion concentration"},
        "acid": {"emoji": "🍋", "object": "Sizzling yellow lemon wedge", "topic": "Chemistry", "reason": "Proton donor substance with pH less than 7"},
        "base": {"emoji": "🧼", "object": "Slippery bar of white soap", "topic": "Chemistry", "reason": "Proton acceptor alkaline substance with pH greater than 7"},
        "catalyst": {"emoji": "🏎️", "object": "Turbocharger pedal on a chemical cart", "topic": "Chemistry", "reason": "Agent lowering activation energy without being consumed"},
        "activation energy": {"emoji": "🧗", "object": "Steep rocky hill to climb before sliding", "topic": "Chemistry", "reason": "Minimum threshold energy required to initiate a reaction"},
        "exothermic": {"emoji": "🔥", "object": "Crackling campfire radiating warmth", "topic": "Chemistry", "reason": "Chemical reaction releasing net thermal energy to surroundings"},
        "endothermic": {"emoji": "🧊", "object": "Freezing ice pack absorbing surrounding heat", "topic": "Chemistry", "reason": "Chemical reaction absorbing thermal energy from surroundings"},
        "solution": {"emoji": "☕", "object": "Clear cup with dissolved sugar syrup", "topic": "Chemistry", "reason": "Homogeneous mixture of solute completely dissolved in solvent"},
        "solute": {"emoji": "🧂", "object": "Pinch of fine white sea salt", "topic": "Chemistry", "reason": "Substance being dissolved into a larger liquid medium"},
        "solvent": {"emoji": "🫗", "object": "Glass beaker of pure liquid water", "topic": "Chemistry", "reason": "Dissolving medium holding solute particles in suspension"},
        "periodic table": {"emoji": "📊", "object": "Grid mosaic of colorful element tiles", "topic": "Chemistry", "reason": "Systematic tabular arrangement of elements by atomic number"},
        "oxidation": {"emoji": "🔩", "object": "Rusty flaking iron nail", "topic": "Chemistry", "reason": "Loss of electrons or increase in oxidation state"},
        "reduction": {"emoji": "🪙", "object": "Polished bright copper coin", "topic": "Chemistry", "reason": "Gain of electrons or decrease in oxidation state"},
        "redox": {"emoji": "⚖️", "object": "Seesaw exchanging electron balls", "topic": "Chemistry", "reason": "Coupled reduction-oxidation electron transfer reaction"},
        "isotope": {"emoji": "👯", "object": "Twin dolls with one wearing a heavy backpack", "topic": "Chemistry", "reason": "Nuclides of same element with different neutron numbers"},
        "avogadros number": {"emoji": "🔢", "object": "Enormous sack holding 6.022x10^23 beans", "topic": "Chemistry", "reason": "Number of constituent particles in exactly one mole"},
        "mole": {"emoji": "📦", "object": "Standard counting crate for chemicals", "topic": "Chemistry", "reason": "Standard SI unit measuring amount of substance"},
        "titration": {"emoji": "💧", "object": "Graduated glass burette dripping single drops", "topic": "Chemistry", "reason": "Volumetric analytical method using indicator endpoint"},
        "equilibrium": {"emoji": "🤹", "object": "Juggler keeping two equal spinning plates", "topic": "Chemistry", "reason": "Forward and reverse reaction rates balancing dynamically"},
        "le chateliers principle": {"emoji": "⚖️", "object": "Counterweight restoring a tipped balance", "topic": "Chemistry", "reason": "System counteracting external stresses to restore balance"},
        "electronegativity": {"emoji": "🧲", "object": "Greedy magnet pulling electron blankets", "topic": "Chemistry", "reason": "Tendency of an atom to attract shared electron pairs"},
        "malleability": {"emoji": "🔨", "object": "Pounded golden foil sheet", "topic": "Chemistry", "reason": "Ability of metal to deform under compressive stress"},
        "ductility": {"emoji": "🧵", "object": "Thin copper wire spool", "topic": "Chemistry", "reason": "Ability of metal to stretch into elongated wire strands"},
        "polymer": {"emoji": "📿", "object": "Long necklace of interlocking colored beads", "topic": "Chemistry", "reason": "Macromolecule composed of repeating monomer subunits"},
        "monomer": {"emoji": "📿", "object": "Single clip-on plastic bead", "topic": "Chemistry", "reason": "Small individual unit that polymerizes into chains"},
        "distillation": {"emoji": "⚗️", "object": "Curved glass condenser separating steam", "topic": "Chemistry", "reason": "Thermal separation technique based on boiling points"},
        "crystallization": {"emoji": "💎", "object": "Geometric quartz crystal blooming in jar", "topic": "Chemistry", "reason": "Solute precipitating into orderly crystalline lattice"},
        "colloid": {"emoji": "🥛", "object": "Glass of rich cloudy milk scattering laser beam", "topic": "Chemistry", "reason": "Microscopic insoluble particles suspended through medium"},

        # Computer Science (40 entries)
        "tcp/ip model": {"emoji": "📦", "object": "Four-tier stacked postal conveyor belt", "topic": "Computer Science", "reason": "Foundational suite of layered protocols connecting the internet"},
        "application layer": {"emoji": "📱", "object": "Smartphone loaded with glowing app icons", "topic": "Computer Science", "reason": "Top layer interfacing directly with user software like HTTP"},
        "transport layer": {"emoji": "🚚", "object": "Reliable yellow delivery truck", "topic": "Computer Science", "reason": "Ensures end-to-end data delivery and sequencing via TCP/UDP"},
        "internet layer": {"emoji": "🌐", "object": "Spinning illuminated globe map", "topic": "Computer Science", "reason": "Routes data packets across multiple networks using IP"},
        "network-access layer": {"emoji": "📶", "object": "Blinking Wi-Fi router and ethernet jack", "topic": "Computer Science", "reason": "Physical and data link handling bits over copper or air"},
        "algorithm": {"emoji": "📜", "object": "Step-by-step master chef recipe scroll", "topic": "Computer Science", "reason": "Well-defined sequential procedure for solving a computational problem"},
        "binary": {"emoji": "🎛️", "object": "Row of glowing 0 and 1 toggle switches", "topic": "Computer Science", "reason": "Base-2 numeral system powering modern digital electronics"},
        "cpu": {"emoji": "🧠", "object": "Microchip with miniature ticking golden gears", "topic": "Computer Science", "reason": "Central processing unit executing instruction cycles"},
        "ram": {"emoji": "🗄️", "object": "Row of clear glass drawers for quick retrieval", "topic": "Computer Science", "reason": "Volatile high-speed temporary memory for active tasks"},
        "cache": {"emoji": "⚡", "object": "Pocket holster with instant access darts", "topic": "Computer Science", "reason": "Ultra-fast tiny memory holding frequently needed data"},
        "database": {"emoji": "🗃️", "object": "Steel archive filing cabinet with electronic locks", "topic": "Computer Science", "reason": "Structured collection of indexed and queryable information"},
        "sql": {"emoji": "🔍", "object": "Magnifying glass pointing at tabular spreadsheets", "topic": "Computer Science", "reason": "Standard declarative query language for relational data"},
        "stack": {"emoji": "🥞", "object": "Tall stack of fluffy breakfast pancakes (LIFO)", "topic": "Computer Science", "reason": "Last-in First-out linear data structure"},
        "queue": {"emoji": "🎟️", "object": "Orderly movie ticket queue line (FIFO)", "topic": "Computer Science", "reason": "First-in First-out sequential waiting line"},
        "linked list": {"emoji": "🚂", "object": "Toy train with cars hooked by magnetic couplings", "topic": "Computer Science", "reason": "Chain of independent data nodes each pointing to the next"},
        "binary tree": {"emoji": "🌳", "object": "Bifurcating wooden tree with two branches per node", "topic": "Computer Science", "reason": "Hierarchical data structure branching into left and right subtrees"},
        "graph": {"emoji": "🕸️", "object": "Network of glowing glass spheres linked by cords", "topic": "Computer Science", "reason": "Collection of vertices connected by directional or weighted edges"},
        "hash table": {"emoji": "🏷️", "object": "Key rack with labeled pigeonhole slots", "topic": "Computer Science", "reason": "Associative array mapping hashed keys to bucket values in O(1)"},
        "recursion": {"emoji": "🪆", "object": "Russian nesting doll opening into smaller copies", "topic": "Computer Science", "reason": "Function repeatedly calling itself until reaching base case"},
        "sorting": {"emoji": "📚", "object": "Librarian arranging mismatched books by height", "topic": "Computer Science", "reason": "Algorithmic ordering of elements into ascending order"},
        "compiler": {"emoji": "🔄", "object": "Magic translation machine converting script to gears", "topic": "Computer Science", "reason": "Translates high-level source code into executable machine code"},
        "operating system": {"emoji": "🚦", "object": "Traffic conductor waving flags at intersections", "topic": "Computer Science", "reason": "Core software managing system hardware and resource allocation"},
        "deadlock": {"emoji": "🔒", "object": "Four cars blocking each other in a cross-intersection", "topic": "Computer Science", "reason": "Circular wait state where processes freeze awaiting resources"},
        "encryption": {"emoji": "🔐", "object": "Iron padlock securing a secret cipher box", "topic": "Computer Science", "reason": "Cryptographic transformation scrambling plaintext into ciphertext"},
        "firewall": {"emoji": "🧱", "object": "Flame-retardant brick wall filtering incoming traffic", "topic": "Computer Science", "reason": "Security barrier inspecting packets against firewall rules"},
        "object-oriented programming": {"emoji": "🧱", "object": "Modular LEGO building kit with blueprints and parts", "topic": "Computer Science", "reason": "Paradigm modeling software as classes with encapsulated state"},
        "inheritance": {"emoji": "👑", "object": "Child wearing an ancestral golden crown", "topic": "Computer Science", "reason": "Subclass deriving properties and methods from parent class"},
        "polymorphism": {"emoji": "🦎", "object": "Chameleon adapting color to its environment", "topic": "Computer Science", "reason": "Single interface representing differing underlying forms"},
        "concurrency": {"emoji": "🤹", "object": "Circus performer juggling multiple balls at once", "topic": "Computer Science", "reason": "Executing multiple tasks in overlapping time periods"},
        "thread": {"emoji": "🧵", "object": "Spool of silver sewing thread running in parallel", "topic": "Computer Science", "reason": "Smallest sequence of programmed instructions managed by OS"},
        "api": {"emoji": "🔌", "object": "Universal electric socket and plug adapter", "topic": "Computer Science", "reason": "Application programming interface mediating software exchanges"},
        "git": {"emoji": "🌿", "object": "Branching family tree with timestamp tags", "topic": "Computer Science", "reason": "Distributed version control tracking revisions over time"},
        "cloud computing": {"emoji": "☁️", "object": "Glowing digital cloud showering data onto laptops", "topic": "Computer Science", "reason": "On-demand availability of remote computer system resources"},
        "machine learning": {"emoji": "🤖", "object": "Robot studying textbooks and getting smarter", "topic": "Computer Science", "reason": "Algorithms improving performance through empirical data experience"},
        "neural network": {"emoji": "🧠", "object": "Lattice of interconnected LED bulbs blinking together", "topic": "Computer Science", "reason": "Layered computational model inspired by biological nervous systems"},
        "big o notation": {"emoji": "⏱️", "object": "Stopwatch measuring efficiency curves as inputs swell", "topic": "Computer Science", "reason": "Mathematical notation describing asymptotic growth rate"},
        "pointer": {"emoji": "👉", "object": "Foam pointing finger aimed at a memory address", "topic": "Computer Science", "reason": "Variable holding direct memory address of another value"},
        "garbage collection": {"emoji": "🧹", "object": "Autonomous cleaning broom sweeping unused heap memory", "topic": "Computer Science", "reason": "Automatic memory management freeing unreferenced memory"},
        "virtual machine": {"emoji": "📦", "object": "Computer running inside a transparent glass box", "topic": "Computer Science", "reason": "Software emulation of complete physical computer architecture"},
        "dns": {"emoji": "📖", "object": "Thick phone directory translating names to numbers", "topic": "Computer Science", "reason": "Domain Name System resolving human URLs to numerical IP addresses"},

        # Mathematics (35 entries)
        "calculus": {"emoji": "📈", "object": "Curved slope with infinite stepping stones", "topic": "Maths", "reason": "Mathematical study of continuous change and accumulation"},
        "derivative": {"emoji": "📐", "object": "Tangent ruler skimming the steepness of a hill", "topic": "Maths", "reason": "Instantaneous rate of change of a mathematical function"},
        "integral": {"emoji": "🧱", "object": "Stack of microscopic bricks filling the area under a curve", "topic": "Maths", "reason": "Accumulated continuous area under a curve boundary"},
        "matrix": {"emoji": "🪟", "object": "Window pane grid containing numbers in each pane", "topic": "Maths", "reason": "Rectangular numerical array subjected to linear algebra"},
        "vector": {"emoji": "🏹", "object": "Glowing compass arrow with defined length", "topic": "Maths", "reason": "Geometric entity having both magnitude and direction"},
        "probability": {"emoji": "🎲", "object": "Pair of rolling red casino dice", "topic": "Maths", "reason": "Numerical measure of likelihood that an event will occur"},
        "statistics": {"emoji": "📊", "object": "Barbell bell curve diagram on a whiteboard", "topic": "Maths", "reason": "Science of collecting, analyzing, and interpreting sample data"},
        "prime number": {"emoji": "💎", "object": "Indivisible solid diamond block", "topic": "Maths", "reason": "Integer greater than 1 divisible only by 1 and itself"},
        "fibonacci sequence": {"emoji": "🐚", "object": "Spiraling nautilus shell", "topic": "Maths", "reason": "Numerical sequence where each term sums the previous two"},
        "pythagorean theorem": {"emoji": "📐", "object": "Right triangle with square tiles on each side", "topic": "Maths", "reason": "Geometric relation stating a^2 + b^2 = c^2 for right triangles"},
        "pi": {"emoji": "🥧", "object": "Golden circular pie wrapped with tape", "topic": "Maths", "reason": "Irrational ratio of circle circumference to its diameter"},
        "euler number": {"emoji": "📈", "object": "Exponential money tree sprouting continuously", "topic": "Maths", "reason": "Base of natural logarithm representing continuous compound growth"},
        "logarithm": {"emoji": "🪜", "object": "Ladder where each step multiplies height tenfold", "topic": "Maths", "reason": "Inverse power function answering what exponent reaches target"},
        "standard deviation": {"emoji": "📏", "object": "Ruler measuring spread of darts around bullseye", "topic": "Maths", "reason": "Measure of dispersion of a dataset relative to its mean"},
        "mean": {"emoji": "⚖️", "object": "Fulcrum balancing uneven weights evenly", "topic": "Maths", "reason": "Arithmetic average summing elements divided by count"},
        "median": {"emoji": "🛣️", "object": "Painted center divider strip down a highway", "topic": "Maths", "reason": "Middle value separating top half of sorted sample from bottom"},
        "variance": {"emoji": "🎯", "object": "Scattered arrow marks around a center ring", "topic": "Maths", "reason": "Average squared deviation of data points from the sample mean"},
        "normal distribution": {"emoji": "🔔", "object": "Symmetrical brass church bell", "topic": "Maths", "reason": "Classic bell curve where values cluster near mean symmetrically"},
        "eigenvalue": {"emoji": "📏", "object": "Rubber band stretching without changing its orientation", "topic": "Maths", "reason": "Scalar factor by which an eigenvector is stretched in transform"},
        "determinant": {"emoji": "📦", "object": "Box whose volume scales with grid distortion", "topic": "Maths", "reason": "Scalar scaling factor of the linear transformation of a matrix"},
        "set theory": {"emoji": "⭕", "object": "Overlapping Venn diagram hula hoops", "topic": "Maths", "reason": "Branch of logic studying collections of distinct objects"},
        "polynomial": {"emoji": "🎢", "object": "Roller coaster with multiple ascending hills and drops", "topic": "Maths", "reason": "Algebraic expression composed of variables and coefficients"},
        "factorial": {"emoji": "❗", "object": "Row of multiplying cascading falling dominos", "topic": "Maths", "reason": "Product of an integer and all positive integers below it"},
        "limit": {"emoji": "🛑", "object": "Barrier wall that footsteps approach infinitely close to", "topic": "Maths", "reason": "Value a function approaches as input nears a specific point"},
        "asymptote": {"emoji": "🛤️", "object": "Parallel train track that curves near but never touches", "topic": "Maths", "reason": "Line that a curve approaches indefinitely without intersecting"},
        "hypothesis testing": {"emoji": "⚖️", "object": "Courtroom gavel evaluating statistical evidence", "topic": "Maths", "reason": "Formal procedure for assessing whether data supports a claim"},
        "p-value": {"emoji": "🎟️", "object": "Scratch lottery ticket showing probability of chance", "topic": "Maths", "reason": "Probability of observing results as extreme under null hypothesis"},
        "correlation": {"emoji": "🪢", "object": "Two dancing ribbons twirling in synchrony", "topic": "Maths", "reason": "Statistical association measuring mutual co-movement"},
        "regression": {"emoji": "📉", "object": "Straight neon line fitted through scattered points", "topic": "Maths", "reason": "Statistical modeling of relationships between dependent and predictor vars"},
        "topology": {"emoji": "🍩", "object": "Clay doughnut stretching into a coffee mug", "topic": "Maths", "reason": "Study of geometric properties preserved under continuous deformation"},
        "trigonometry": {"emoji": "📐", "object": "Sextant measuring angle of stars above sea", "topic": "Maths", "reason": "Branch relating angles and side lengths of geometric triangles"},
        "imaginary number": {"emoji": "🦄", "object": "Unicorn horn emerging from square root of negative one", "topic": "Maths", "reason": "Complex number unit i defined such that i squared equals -1"},
        "infinity": {"emoji": "♾️", "object": "Figure-eight racetrack with no finish line", "topic": "Maths", "reason": "Concept describing something without bound or end"},
        "permutation": {"emoji": "🔀", "object": "Combination lock dialing specific ordered numbers", "topic": "Maths", "reason": "Ordered arrangement of a set of items where sequence matters"},
        "combination": {"emoji": "🥗", "object": "Salad bowl where ingredients mix without ordering", "topic": "Maths", "reason": "Selection of items from a collection where order does not matter"},

        # History (30 entries)
        "industrial revolution": {"emoji": "🚂", "object": "Steam train billowing black smoke past brick factories", "topic": "History", "reason": "Transition to powered machinery and factory manufacturing"},
        "french revolution": {"emoji": "🏰", "object": "Stormed stone bastille fortress with tricolor flag", "topic": "History", "reason": "Epochal uprising overthrowing the Bourbon monarchy in 1789"},
        "world war i": {"emoji": "🪖", "object": "Muddy trench helmet wrapped in barbed wire", "topic": "History", "reason": "Global conflict characterized by trench warfare from 1914-1918"},
        "world war ii": {"emoji": "✈️", "object": "Radar screen tracking fleets across ocean", "topic": "History", "reason": "Global war spanning 1939-1945 ending with atomic age"},
        "cold war": {"emoji": "🧊", "object": "Divided concrete wall under surveillance spotlight", "topic": "History", "reason": "Decades of geopolitical tension between US and Soviet blocs"},
        "renaissance": {"emoji": "🎨", "object": "Leonardo da Vinci sketch easel in Florence", "topic": "History", "reason": "Cultural rebirth of art, science, and classical humanism"},
        "enlightenment": {"emoji": "🕯️", "object": "Lit oil lamp resting on philosophical treatises", "topic": "History", "reason": "Intellectual movement emphasizing reason, liberty, and science"},
        "magna carta": {"emoji": "📜", "object": "Feudal parchment bearing royal wax seal", "topic": "History", "reason": "1215 English charter establishing rule of law over monarchy"},
        "roman empire": {"emoji": "🏛️", "object": "Colosseum amphitheater with marching legion banner", "topic": "History", "reason": "Imperial civilization dominating Mediterranean world for centuries"},
        "ancient egypt": {"emoji": "🏺", "object": "Golden pharaoh mask beside sandstone pyramid", "topic": "History", "reason": "Nile civilization renowned for pharaohs, mummification, and hieroglyphs"},
        "silk road": {"emoji": "🐫", "object": "Caravan camel loaded with spices and embroidered silk", "topic": "History", "reason": "Ancient overland trade routes linking East Asia and Europe"},
        "colonialism": {"emoji": "🧭", "object": "Caravel galleon claiming foreign shores on map", "topic": "History", "reason": "Practice of acquiring political and territorial control over peoples"},
        "democracy": {"emoji": "🗳️", "object": "Wooden ballot box with citizens casting marked tokens", "topic": "History", "reason": "System of governance where authority derives from citizens"},
        "monarchy": {"emoji": "👑", "object": "Jeweled golden crown resting on velvet throne", "topic": "History", "reason": "Form of government with a monarch or royal dynasty at head"},
        "feudalism": {"emoji": "🛡️", "object": "Knight in plate armor kneeling before manor castle", "topic": "History", "reason": "Medieval social hierarchy based on landholding and vassal allegiance"},
        "treaty of versailles": {"emoji": "🖋️", "object": "Gold fountain pen signing 1919 peace accord", "topic": "History", "reason": "Peace treaty concluding WWI and imposing terms on Germany"},
        "great depression": {"emoji": "📉", "object": "Cracked stock market ticker tape from 1929", "topic": "History", "reason": "Severe global economic downturn throughout 1930s decade"},
        "united nations": {"emoji": "🕊️", "object": "Olive branch emblem surrounded by national flags", "topic": "History", "reason": "International organization founded in 1945 for peace and security"},
        "apartheid": {"emoji": "🚧", "object": "Segregation barrier fence dividing a street", "topic": "History", "reason": "System of institutional racial segregation in South Africa"},
        "space race": {"emoji": "🚀", "object": "Apollo lunar module standing on moon dust", "topic": "History", "reason": "Cold War technological rivalry culminating in lunar landing"},
        "glorious revolution": {"emoji": "👑", "object": "Parliamentary parchment limiting royal powers", "topic": "History", "reason": "1688 British transition establishing constitutional monarchy"},
        "american revolution": {"emoji": "🔔", "object": "Cracked Liberty Bell tolling freedom", "topic": "History", "reason": "Thirteen colonies winning sovereignty from British crown"},
        "printing press": {"emoji": "📰", "object": "Gutenberg wooden press stamping movable metal type", "topic": "History", "reason": "Invention democratizing literacy and distribution of ideas"},
        "black death": {"emoji": "🐀", "object": "Beaked plague doctor mask on medieval cobblestones", "topic": "History", "reason": "Devastating 14th-century bubonic plague pandemic in Eurasia"},
        "crusades": {"emoji": "⚔️", "object": "Red cross banner carried along desert fortress walls", "topic": "History", "reason": "Medieval religious military campaigns into the Holy Land"},
        "reformation": {"emoji": "🔨", "object": "Ninety-five theses nailed to heavy wooden cathedral doors", "topic": "History", "reason": "16th-century religious challenge splintering Western Christianity"},
        "columbian exchange": {"emoji": "🌽", "object": "Crate exchanging American corn and European wheat", "topic": "History", "reason": "Widespread transfer of crops, animals, and pathogens after 1492"},
        "scramble for africa": {"emoji": "🗺️", "object": "Berlin conference table slicing continent map with ruler", "topic": "History", "reason": "Late 19th-century European invasion and colonization of Africa"},
        "berlin wall": {"emoji": "🧱", "object": "Graffiti-painted concrete barrier crumbling under sledgehammers", "topic": "History", "reason": "Physical divide falling in 1989 marking the end of Cold War division"},
        "decolonization": {"emoji": "🚩", "object": "Lowering colonial ensign and raising new national flag", "topic": "History", "reason": "Post-WWII undoing of colonialism across Asia and Africa"},

        # General / Cognitive Science (20 entries)
        "memory palace": {"emoji": "🏛️", "object": "Grand architectural villa with numbered luminous doorways", "topic": "General", "reason": "Method of Loci spatial framework for anchoring mental associations"},
        "spaced repetition": {"emoji": "📅", "object": "Calendar notebook with reminder flags on expanding intervals", "topic": "General", "reason": "Learning technique spacing reviews across increasing time windows"},
        "active recall": {"emoji": "❓", "object": "Flashcard with question facing forward and answer covered", "topic": "General", "reason": "Testing retrieval from memory rather than passively reviewing notes"},
        "forgetting curve": {"emoji": "📉", "object": "Ebbinghaus slide showing memories slipping down a ramp", "topic": "General", "reason": "Hypothesized exponential decay of memory retention over time"},
        "retrieval practice": {"emoji": "🎣", "object": "Fishing rod pulling shiny memory keys from deep water", "topic": "General", "reason": "Deliberate effort to recall stored knowledge strengthening neural pathways"},
        "cognitive load": {"emoji": "🎒", "object": "Heavy hiker backpack packed to the brim with books", "topic": "General", "reason": "Total amount of working memory resources used in learning"},
        "working memory": {"emoji": "📝", "object": "Small sticky notepad with room for seven quick notes", "topic": "General", "reason": "System holding temporary information for immediate reasoning"},
        "long term memory": {"emoji": "🏦", "object": "Deep underground vault lined with steel lockboxes", "topic": "General", "reason": "Permanent brain repository storing knowledge indefinitely"},
        "neuroplasticity": {"emoji": "🌱", "object": "Garden vines weaving new pathways through a trellis", "topic": "General", "reason": "Brain capacity to adapt and reorganize neural connections"},
        "mnemonic": {"emoji": "🔑", "object": "Golden skeleton key unlocking an associative riddle", "topic": "General", "reason": "Cognitive tool assisting memory retention and quick retrieval"},
        "water cycle": {"emoji": "🌧️", "object": "Looping glass tube cycling steam into rain into rivers", "topic": "General", "reason": "Continuous planetary movement of water through atmosphere and land"},
        "evaporation": {"emoji": "♨️", "object": "Steaming kettle turning puddle into rising vapor", "topic": "General", "reason": "Phase transition of liquid turning into atmospheric vapor"},
        "condensation": {"emoji": "🪟", "object": "Dewy foggy window pane forming droplets", "topic": "General", "reason": "Phase change from atmospheric gas into liquid water droplets"},
        "precipitation": {"emoji": "🌧️", "object": "Shower of falling raindrops on an umbrella", "topic": "General", "reason": "Condensed water vapor falling under gravity as rain or snow"},
        "collection": {"emoji": "🏞️", "object": "Still mountain lake gathering flowing streams", "topic": "General", "reason": "Precipitation accumulating in reservoirs, oceans, and groundwater"},
        "metacognition": {"emoji": "🪞", "object": "Reflective mirror where a thinker watches their own thought process", "topic": "General", "reason": "Higher-order awareness and understanding of one's own learning"},
        "consolidation": {"emoji": "🧱", "object": "Fresh wet cement hardening overnight into solid stone", "topic": "General", "reason": "Post-learning stabilization converting labile memories into long-term traces"},
        "priming": {"emoji": "🎯", "object": "Lightly tapped cue ball setting up the target pocket", "topic": "General", "reason": "Implicit effect where exposure to a stimulus influences response to a later one"},
        "interference": {"emoji": "📻", "object": "Crackling radio dial where two stations overlap", "topic": "General", "reason": "Disruption of memory storage or retrieval caused by competing information"},
        "chunking": {"emoji": "🍱", "object": "Bento lunchbox dividing scattered food into neat compartments", "topic": "General", "reason": "Grouping individual bits of information into meaningful, manageable units"}
    }

    os.makedirs("data", exist_ok=True)
    with open("data/concept_visual_dictionary.json", "w", encoding="utf-8") as f:
        json.dump(dictionary, f, indent=2, ensure_ascii=False)
    print(f"Generated data/concept_visual_dictionary.json with {len(dictionary)} curated concepts.")
    return dictionary

def generate_concepts_seed(dictionary):
    """
    Generate data/concepts_seed.csv with at least 320 labelled rows across 7 topics.
    Labels: Easy, Medium, Hard.
    """
    topics_list = ["Biology", "Physics", "Chemistry", "Computer Science", "Maths", "History", "General"]
    
    # Base concept entries from dictionary
    rows = []
    for concept, meta in dictionary.items():
        topic = meta["topic"]
        # Determine difficulty heuristically based on length and syllables
        length = len(concept)
        words = len(concept.split())
        if words > 2 or length > 16 or any(c in concept for c in ["thermodynamics", "schrodinger", "endoplasmic", "superconductivity", "polymorphism", "le chatelier", "eigenvalue", "asymptote"]):
            difficulty = "Hard"
        elif words == 2 or length > 8:
            difficulty = "Medium"
        else:
            difficulty = "Easy"
            
        context = f"{concept.capitalize()} is a fundamental concept in {topic} explaining {meta['reason'].lower()}."
        rows.append({
            "concept": concept,
            "topic": topic,
            "difficulty": difficulty,
            "context_sentence": context,
            "word_count": words,
            "char_length": length
        })

    # Supplementary concepts to ensure >= 320 rows across all 7 topics
    supplementary = [
        # Biology additions
        ("cellular respiration", "Biology", "Medium", "Cellular respiration produces ATP by oxidizing organic fuel."),
        ("photosystem ii", "Biology", "Hard", "Photosystem II splits water molecules using absorbed photon energy."),
        ("thylakoid", "Biology", "Medium", "Thylakoid membranes contain the pigment complexes of photosynthesis."),
        ("calvin cycle", "Biology", "Medium", "The Calvin cycle fixes inorganic carbon into glyceraldehyde phosphate."),
        ("atp synthase", "Biology", "Hard", "ATP synthase harnesses the proton gradient to synthesize ATP."),
        ("action potential", "Biology", "Medium", "Action potential transmits rapid electrical depolarization along the axon."),
        ("neurotransmitter", "Biology", "Medium", "Neurotransmitter chemicals bridge synaptic clefts to stimulate receptors."),
        ("phagocytosis", "Biology", "Medium", "Phagocytosis allows immune cells to engulf and destroy pathogenic invaders."),
        ("apoptosis", "Biology", "Hard", "Apoptosis is programmed cellular death regulating tissue development."),
        ("translation", "Biology", "Easy", "Translation synthesizes polypeptide chains from mRNA sequences."),
        ("transcription", "Biology", "Easy", "Transcription copies DNA templates into complementary RNA transcripts."),
        ("polymerase", "Biology", "Medium", "DNA polymerase synthesizes daughter strands during DNA replication."),
        ("telomere", "Biology", "Hard", "Telomeres protect linear chromosome ends from progressive degradation."),
        ("epigenetics", "Biology", "Hard", "Epigenetics alters gene expression without modifying nucleotide sequence."),
        ("symbiosis", "Biology", "Easy", "Symbiosis denotes close long-term biological interaction between species."),
        ("predation", "Biology", "Easy", "Predation is an ecological interaction where predator hunts prey."),
        ("parasitism", "Biology", "Easy", "Parasitism involves one organism benefiting at host expense."),

        # Physics additions
        ("angular momentum", "Physics", "Medium", "Angular momentum is conserved in systems with zero external torque."),
        ("special relativity", "Physics", "Hard", "Special relativity predicts Lorentz contraction and relativistic time dilation."),
        ("lorentz force", "Physics", "Hard", "Lorentz force acts on charged particles moving in magnetic fields."),
        ("faradays law", "Physics", "Medium", "Faradays law relates changing magnetic flux to induced electromotive force."),
        ("lenzs law", "Physics", "Medium", "Lenzs law states induced current opposes flux changes that created it."),
        ("snells law", "Physics", "Easy", "Snells law describes wave refraction angles across distinct media boundaries."),
        ("blackbody radiation", "Physics", "Hard", "Blackbody radiation sparked Planck's quantum hypothesis."),
        ("photoelectric effect", "Physics", "Medium", "Photoelectric effect demonstrates light quantization into photons."),
        ("heisenberg uncertainty", "Physics", "Hard", "Uncertainty principle limits simultaneous precision of position and momentum."),
        ("schrodinger equation", "Physics", "Hard", "Schrodinger equation models quantum wave function temporal evolution."),
        ("hookes law", "Physics", "Easy", "Hookes law states spring restoring force is proportional to displacement."),
        ("simple harmonic motion", "Physics", "Medium", "Simple harmonic motion features sinusoidal restorative acceleration."),
        ("gravitational lensing", "Physics", "Hard", "Gravitational lensing bends starlight around massive astronomical bodies."),
        ("coulomb barrier", "Physics", "Hard", "Coulomb barrier prevents positive nuclei from fusing without sufficient energy."),
        ("superposition", "Physics", "Medium", "Superposition allows overlapping linear waves to add constructively."),

        # Chemistry additions
        ("gibbs free energy", "Chemistry", "Hard", "Gibbs free energy determines thermodynamic spontaneity of chemical reactions."),
        ("enthalpy", "Chemistry", "Medium", "Enthalpy measures the total internal energy plus pressure-volume work."),
        ("van der waals forces", "Chemistry", "Medium", "Van der Waals forces are transient intermolecular attractions between neutral dipoles."),
        ("hybridization", "Chemistry", "Hard", "Orbital hybridization mixes atomic orbitals into equivalent hybrid geometries."),
        ("resonance structure", "Chemistry", "Medium", "Resonance structures describe delocalized bonding across conjugated pi systems."),
        ("electrolysis", "Chemistry", "Easy", "Electrolysis drives non-spontaneous reactions via electrical current."),
        ("galvanic cell", "Chemistry", "Medium", "Galvanic cells generate electrical voltage through spontaneous redox reactions."),
        ("buffer solution", "Chemistry", "Medium", "Buffer solutions resist drastic pH shifts when small acid or base is added."),
        ("stoichiometry", "Chemistry", "Medium", "Stoichiometry calculates quantitative mass proportions of reacting chemical species."),
        ("ideal gas law", "Chemistry", "Easy", "Ideal gas law relates pressure, volume, moles, and temperature via PV=nRT."),
        ("boiling point elevation", "Chemistry", "Medium", "Colligative property where non-volatile solute raises solvent boiling point."),
        ("electrophile", "Chemistry", "Hard", "Electrophiles are electron-deficient species accepting electron pairs in reactions."),
        ("nucleophile", "Chemistry", "Hard", "Nucleophiles donate electron pairs to form covalent bonds with electrophiles."),
        ("isomer", "Chemistry", "Easy", "Isomers share molecular formulas but differ in structural atomic arrangement."),
        ("chirality", "Chemistry", "Hard", "Chiral molecules possess non-superimposable mirror images known as enantiomers."),

        # Computer Science additions
        ("turing machine", "Computer Science", "Hard", "Turing machines are theoretical abstract mathematical models of general computation."),
        ("np-completeness", "Computer Science", "Hard", "NP-complete problems have polynomial verification but intractable known solutions."),
        ("dijkstras algorithm", "Computer Science", "Medium", "Dijkstras algorithm computes shortest paths in non-negative weighted graphs."),
        ("breadth-first search", "Computer Science", "Easy", "Breadth-first search traverses graphs layer by layer using a FIFO queue."),
        ("depth-first search", "Computer Science", "Easy", "Depth-first search traverses branches deeply using recursion or a LIFO stack."),
        ("dynamic programming", "Computer Science", "Hard", "Dynamic programming solves optimization tasks by caching overlapping subproblem solutions."),
        ("merge sort", "Computer Science", "Medium", "Merge sort recursively divides arrays and merges sorted halves in O(n log n)."),
        ("quick sort", "Computer Science", "Medium", "Quick sort partitions elements around a pivot value for efficient sorting."),
        ("b-tree", "Computer Science", "Hard", "B-trees maintain balanced multiway disk-optimized indexing in production databases."),
        ("asymmetric encryption", "Computer Science", "Hard", "Asymmetric cryptography utilizes public-private keypairs for secure communication."),
        ("jwt token", "Computer Science", "Medium", "JSON Web Tokens represent claims securely transmitted between client and server."),
        ("rest api", "Computer Science", "Easy", "REST architectural style structures web communication around stateless resource URLs."),
        ("graphql", "Computer Science", "Medium", "GraphQL allows clients to request exact declarative data schemas in single requests."),
        ("docker container", "Computer Science", "Medium", "Docker containers package code with isolated OS-level dependencies."),
        ("kubernetes", "Computer Science", "Hard", "Kubernetes automates container deployment, scaling, and operational management."),
        ("mapreduce", "Computer Science", "Hard", "MapReduce processes massive distributed datasets across commodity computing clusters."),
        ("semantic web", "Computer Science", "Medium", "Semantic web enriches internet documents with structured machine-readable metadata."),

        # Mathematics additions
        ("fourier transform", "Maths", "Hard", "Fourier transform decomposes time-domain functions into constituent frequency components."),
        ("laplace transform", "Maths", "Hard", "Laplace transform maps differential equations into algebraic s-domain equations."),
        ("taylor series", "Maths", "Medium", "Taylor series approximates differentiable functions using infinite polynomial sums."),
        ("central limit theorem", "Maths", "Medium", "Central limit theorem proves sample means converge to normal distributions."),
        ("bayes theorem", "Maths", "Medium", "Bayes theorem updates prior conditional probabilities given fresh observed evidence."),
        ("markov chain", "Maths", "Hard", "Markov chains model stochastic state transitions governed only by the current state."),
        ("differential equation", "Maths", "Medium", "Differential equations relate functions to rates of change of their variables."),
        ("complex conjugate", "Maths", "Easy", "Complex conjugate reflects complex numbers across the real Cartesian axis."),
        ("dot product", "Maths", "Easy", "Dot product multiplies directional magnitudes to return scalar algebraic projection."),
        ("cross product", "Maths", "Medium", "Cross product computes orthogonal vectors whose magnitude equals parallelogram area."),
        ("gradient descent", "Maths", "Medium", "Gradient descent iteratively adjusts parameters along the negative loss surface slope."),
        ("convex optimization", "Maths", "Hard", "Convex optimization guarantees any local minimum corresponds to global minimum."),
        ("linear independence", "Maths", "Medium", "Linear independence ensures no vector in a set is a linear combination of others."),
        ("orthogonal matrix", "Maths", "Hard", "Orthogonal matrices preserve vector lengths and Euclidean angles under transformation."),
        ("jacobian matrix", "Maths", "Hard", "Jacobian matrix collects all first-order partial derivatives of vector-valued functions."),

        # History additions
        ("pax romana", "History", "Medium", "Pax Romana was an era of imperial peace and stability across the Roman Empire."),
        ("byzantine empire", "History", "Medium", "The Byzantine Empire preserved Roman administrative law and Greco-Christian culture."),
        ("ottoman empire", "History", "Medium", "The Ottoman Empire controlled strategic Eurasian trade crossroads from Constantinople."),
        ("meiji restoration", "History", "Hard", "The Meiji Restoration accelerated modern industrialization and centralization in Japan."),
        ("opium wars", "History", "Medium", "The Opium Wars forced trade concessions and territorial treaties on Qing China."),
        ("bolshevik revolution", "History", "Medium", "The 1917 Bolshevik Revolution established Soviet socialist governance in Russia."),
        ("marshall plan", "History", "Easy", "The Marshall Plan financed European economic reconstruction after World War II."),
        ("cuban missile crisis", "History", "Medium", "The 1962 Cuban Missile Crisis brought the superpowers to the brink of nuclear war."),
        ("watergate scandal", "History", "Easy", "The Watergate scandal prompted the unprecedented resignation of President Nixon."),
        ("fall of constantinople", "History", "Medium", "The 1453 Fall of Constantinople closed classical European land routes to Asia."),
        ("habeas corpus", "History", "Medium", "Habeas corpus protects individuals against unlawful and arbitrary state detention."),
        ("suffrage movement", "History", "Easy", "The suffrage movement fought for universal voting rights across modern democracies."),
        ("enclosure acts", "History", "Hard", "Enclosure acts privatized common lands, driving agricultural labor to industrial cities."),
        ("congress of vienna", "History", "Hard", "The 1815 Congress of Vienna restored European balance of power after Napoleon."),
        ("vietnam war", "History", "Easy", "The Vietnam War was a Cold War proxy conflict in Southeast Asia from 1955-1975."),

        # General additions
        ("spaced learning", "General", "Easy", "Spaced learning distributes study sessions over time for better memory retention."),
        ("dual coding theory", "General", "Medium", "Dual coding theory posits that verbal and visual information are processed distinctly."),
        ("elaboration", "General", "Easy", "Elaboration connects new knowledge to existing cognitive frameworks."),
        ("metamemory", "General", "Medium", "Metamemory denotes self-awareness of one's own memory abilities and strategies."),
        ("serial position effect", "General", "Medium", "Serial position effect causes best recall for items at the start and end of lists."),
        ("primacy effect", "General", "Easy", "Primacy effect grants superior memory recall to the initial items in a list."),
        ("recency effect", "General", "Easy", "Recency effect boosts recall for the most recently presented study items."),
        ("state-dependent memory", "General", "Medium", "Recall is boosted when psychological state during retrieval matches encoding."),
        ("context-dependent memory", "General", "Medium", "Environmental cues present during encoding facilitate downstream retrieval."),
        ("semantic encoding", "General", "Easy", "Semantic encoding translates sensory information into meaningful conceptual schemas."),
        ("declarative memory", "General", "Easy", "Declarative memory stores conscious facts and knowledge that can be explicitly verbalized."),
        ("procedural memory", "General", "Easy", "Procedural memory stores motor skills and habits that execute automatically."),
        ("episodic memory", "General", "Easy", "Episodic memory preserves personally experienced events tied to time and place."),
        ("flashbulb memory", "General", "Medium", "Flashbulb memories are vivid, highly detailed recollections of emotionally shocking events."),
        ("source amnesia", "General", "Hard", "Source amnesia allows remembering factual information while forgetting where it was learned.")
    ]

    for item in supplementary:
        concept, topic, diff, sentence = item
        rows.append({
            "concept": concept,
            "topic": topic,
            "difficulty": diff,
            "context_sentence": sentence,
            "word_count": len(concept.split()),
            "char_length": len(concept)
        })

    # Save to data/concepts_seed.csv
    with open("data/concepts_seed.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["concept", "topic", "difficulty", "context_sentence", "word_count", "char_length"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated data/concepts_seed.csv with {len(rows)} labelled concepts across {len(topics_list)} topics.")
    return rows

def generate_recall_logs_seed(concepts):
    """
    Generate data/recall_logs_seed.csv with at least 2200 simulated study logs.
    Features:
    - user_id: anonymous string (e.g. LL-SIM-01 ... LL-SIM-25)
    - concept_id: index or concept name
    - topic: topic category
    - difficulty: Easy, Medium, Hard
    - days_since_last_review: float (0.1 to 30.0)
    - num_reviews: integer (1 to 8)
    - past_accuracy: float (0.2 to 1.0)
    - avg_response_time: float in seconds (1.5 to 18.0)
    - hints_used: integer (0, 1, 2)
    - time_of_day: morning, afternoon, evening, night
    - question_type: typed, mcq, reverse, ordering
    - forgotten: 0 (recalled correctly) or 1 (forgotten/incorrect)
    
    Modelled via Ebbinghaus retention:
    R = exp( - t / S )
    Stability S increases with repetitions and past accuracy, decreases with difficulty.
    """
    logs = []
    num_samples = 2500
    times_of_day = ["morning", "afternoon", "evening", "night"]
    q_types = ["typed", "mcq", "reverse", "ordering"]
    diff_penalty = {"Easy": 0.0, "Medium": 0.35, "Hard": 0.75}

    for i in range(num_samples):
        user_num = (i % 30) + 1
        user_id = f"LL-SIM-{user_num:02d}"
        c = random.choice(concepts)
        concept = c["concept"]
        topic = c["topic"]
        difficulty = c["difficulty"]
        
        num_reviews = random.choices([1, 2, 3, 4, 5, 6, 7, 8], weights=[0.25, 0.22, 0.18, 0.14, 0.10, 0.05, 0.04, 0.02])[0]
        past_acc = min(1.0, max(0.2, random.normalvariate(0.75, 0.15)))
        
        # Interval elapsed in days
        if num_reviews == 1:
            days = random.uniform(0.1, 3.0)
        elif num_reviews <= 3:
            days = random.uniform(1.0, 7.0)
        else:
            days = random.uniform(3.0, 25.0)

        # Hints used
        hints_used = random.choices([0, 1, 2], weights=[0.65, 0.25, 0.10])[0]

        # Calculate stability S (days until retention drops to 1/e)
        # Base stability starts at ~2 days, multiplied by repetitions, modulated by difficulty
        base_s = 2.0 * (1.6 ** (num_reviews - 1)) * (past_acc / 0.8)
        penalty = diff_penalty.get(difficulty, 0.3) + (0.2 * hints_used)
        s = max(0.5, base_s / (1.0 + penalty))
        
        # Retention probability R = exp(-days / s)
        retention_prob = math.exp(-days / s)
        
        # Add slight subjective noise / fatigue
        retention_prob = min(0.98, max(0.05, retention_prob + random.uniform(-0.08, 0.08)))
        
        # Outcome: 1 = forgotten (incorrect), 0 = remembered (correct)
        forgotten = 1 if random.random() > retention_prob else 0
        
        # Response time correlates with difficulty and forgetting
        base_rt = 4.0 + (3.0 if difficulty == "Hard" else 1.5 if difficulty == "Medium" else 0.0)
        if forgotten:
            base_rt += random.uniform(3.0, 8.0)
        avg_rt = round(max(1.2, random.normalvariate(base_rt, 1.8)), 2)

        tod = random.choice(times_of_day)
        q_type = random.choice(q_types)

        logs.append({
            "user_id": user_id,
            "concept": concept,
            "topic": topic,
            "difficulty": difficulty,
            "days_since_last_review": round(days, 2),
            "num_reviews": num_reviews,
            "past_accuracy": round(past_acc, 2),
            "avg_response_time": avg_rt,
            "hints_used": hints_used,
            "time_of_day": tod,
            "question_type": q_type,
            "forgotten": forgotten
        })

    # Save to data/recall_logs_seed.csv with explicit SIMULATED metadata header
    with open("data/recall_logs_seed.csv", "w", newline="", encoding="utf-8") as f:
        # Header comment clearly identifying dataset as simulated
        f.write("# SIMULATED DATASET: Ebbinghaus forgetting curve simulation for bootstrap training.\n")
        f.write("# Generated by scripts/generate_seed_data.py for offline student recall modeling.\n")
        writer = csv.DictWriter(f, fieldnames=[
            "user_id", "concept", "topic", "difficulty", "days_since_last_review",
            "num_reviews", "past_accuracy", "avg_response_time", "hints_used",
            "time_of_day", "question_type", "forgotten"
        ])
        writer.writeheader()
        writer.writerows(logs)

    print(f"Generated data/recall_logs_seed.csv with {len(logs)} simulated study logs.")

if __name__ == "__main__":
    print("=== LociLoom Seed Data Generation Starting ===")
    d = generate_curated_dictionary()
    c = generate_concepts_seed(d)
    generate_recall_logs_seed(c)
    print("=== All Seed Data Generated Successfully ===")
