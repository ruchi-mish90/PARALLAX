from dataclasses import dataclass


@dataclass(frozen=True)
class RepresentationRoute:
    representation: str
    reason: str
    band: int | None = None


class RepresentationRouter:
    """Select the preprocessing representation for a sensor pair."""

    def route(self, pair_features: dict) -> RepresentationRoute:
        sensor_a = str(pair_features.get("sensor_a", "")).upper()
        sensor_b = str(pair_features.get("sensor_b", "")).upper()

        modality = str(
            pair_features.get("modality", "")
        ).lower()

        spectral = bool(
            pair_features.get("spectral", False)
        )

        difficulty = str(
            pair_features.get("difficulty", "")
        ).lower()

        if sensor_a == "IIRS" or sensor_b == "IIRS":
            if spectral or modality in {
                "multispectral",
                "spectral",
            }:
                return RepresentationRoute(
                    representation="spectral_gradient",
                    reason="IIRS spectral information is available",
                )

            band = pair_features.get("band", 160)

            return RepresentationRoute(
                representation="band",
                band=int(band),
                reason="IIRS requires a 2-D spectral-band representation",
            )

        if difficulty in {
            "low_texture",
            "cross_sensor",
            "illumination",
        }:
            return RepresentationRoute(
                representation="gradient",
                reason="Structural gradient representation selected",
            )

        return RepresentationRoute(
            representation="native",
            reason="Native representation selected",
        )

    def route_pair(
        self,
        pair_features: dict,
        matcher_router,
    ):
        """
        Jointly select representation and matcher.

        matcher_router is the existing matcher-routing component;
        its public route(...) method is preserved.
        """
        representation = self.route(pair_features)

        matcher_features = dict(pair_features)
        matcher_features["representation"] = representation.representation

        if representation.band is not None:
            matcher_features["band"] = representation.band

        matcher = matcher_router.route(matcher_features)

        return {
            "representation": representation,
            "matcher": matcher,
        }
