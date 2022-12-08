import argparse

def argparser():
    '''Argument parser'''

    # Initialize
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument("-field",
                        "--field",
                        help="Near or far-field approximation",
                        required=False,
                        default=None,
                        type=str)

    parser.add_argument("-vis",
                        "--vis",
                        help="Visulation argument",
                        required=False,
                        default=None,
                        type=str)

    parser.add_argument("-n",
                        "--num_particles",
                        help="Number of particles to simulated",
                        required=False,
                        default=None,
                        type=int)

    parser.add_argument("-overlaps",
                        "--check_overlaps",
                        help="Check geometry overlaps",
                        default=False,
                        action='store_true')

    parser.add_argument("-secondaries",
                        "--track_secondaries",
                        help="Track secondaries (xrays, electrons, positrons, etc.)",
                        default=False,
                        action='store_true')

    parser.add_argument("-angle",
                        "--angle",
                        help="Set the source direction [theta, phi] in rad",
                        required=False,
                        default=None,
                        nargs=2,
                        type=float)

    parser.add_argument("-E",
                        "--energy",
                        help="Set the source energy in keV",
                        required=False,
                        default=None,
                        nargs="+",
                        type=float)

    parser.add_argument("-healpix",
                        "--healpix",
                        help="Set the source direction with healpix [nside, index]. \
                              You can pass multiple indicies, or -1 for all.",
                        required=False,
                        default=None,
                        nargs='+',
                        type=int)

    parser.add_argument("-seed",
                        "--random_seed",
                        help="Set the random seed for simulation",
                        required=False,
                        default=None,
                        type=int)

    parser.add_argument("-rad",
                        "--radius",
                        help="Set the radius of the largest incident cross-section of the source in cm",
                        required=False,
                        default=None,
                        type=float)

    parser.add_argument("-d",
                        "--distance",
                        help="Set the source distance in cm",
                        required=False,
                        default=None,
                        type=float)

    parser.add_argument("-out",
                        "--output",
                        help="Set the name of the output file",
                        required=False,
                        default=None,
                        type=str)

    parser.add_argument("-mp",
                        "--multiprocess",
                        help="Enable multiprocessing",
                        default=False,
                        action='store_true')

    # Return
    return parser.parse_args()
