from cryptography.hazmat.primitives.asymmetric import ec

__all__ = ["EllipticCurve", "CURVES"]

EllipticCurve = ec.EllipticCurve

CURVES = {
    "secp192r1": ec.SECP192R1(),
    "secp224r1": ec.SECP224R1(),
    "secp256k1": ec.SECP256K1(),
    "secp256r1": ec.SECP256R1(),
    "secp384r1": ec.SECP384R1(),
    "secp521r1": ec.SECP521R1(),
}
