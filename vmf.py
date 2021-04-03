from pathlib import Path

# gross but it works


class Plane():
    _type = "solid"

    directions = ["top", "bottom", "left", "right", "front", "back"]
    uv_maps = {
        "t_b": {"uaxis": [1, 0, 0, 0], "vaxis": [0, -1, 0, 0]},
        "r_l": {"uaxis": [0, 1, 0, 0], "vaxis": [0, 0, -1, 0]},
        "f_b": {"uaxis": [1, 0, 0, 0], "vaxis": [0, 0, -1, 0]},
    }

    def __init__(self, coords=(0, 0, 0), dir="top", material="TILE/WHITE_WALL_STATE"):
        self.coords = coords
        self.dir = dir
        self.mat = material

    def get_coords_string(self):
        return "%s %s %s" % (
            "(%s)" % (" ".join(str(c) for c in self.coords[0])),
            "(%s)" % (" ".join(str(c) for c in self.coords[1])),
            "(%s)" % (" ".join(str(c) for c in self.coords[2])),
        )

    def get_uv(self, dir):
        if(dir in ("top", "bottom")):
            return Plane.uv_maps["t_b"]
        elif(dir in ("left", "right")):
            return Plane.uv_maps["r_l"]
        elif(dir in ("front", "back")):
            return Plane.uv_maps["f_b"]
        else:
            raise Exception("Uknown direction %s" % dir)

    def __repr__(self):
        uv = self.get_uv(self.dir)

        # these are indented weirdly purely so the output file is neat
        return """
		side
		{
			"id" "%s"
			"plane" "%s"
			"material" "%s"
			"uaxis" "%s 0.25"
			"vaxis" "%s 0.25"
			"rotation" "0"
			"lightmapscale" "16"
			"smoothing_groups" "0"
		} """ % (
            Plane.directions.index(self.dir) + 1,
            self.get_coords_string(),
            self.mat,
            "[%s]" % (" ".join(str(i) for i in uv["uaxis"])),
            "[%s]" % (" ".join(str(i) for i in uv["vaxis"])),
        )


class Block():
    _type = "solid"

    def __init__(self, origin=(0, 0, 0), dimensions=(0, 0, 0), material="TILE/WHITE_WALL_STATE"):
        self.dim = dimensions
        self.mat = material
        self.origin = origin

        self.planes = self.generate_planes()

    def generate_planes(self):
        x = self.origin[0]
        y = self.origin[1]
        z = self.origin[2]
        w, l, h = self.dim
        a = w / 2
        b = l / 2
        c = h / 2

        # maf innit
        planes = [
            Plane((
                (x - a, y - b, z + c), (x - a, y + b, z + c), (x + a, y + b, z + c)
            ), "top", self.mat),
            Plane((
                (x - a, y + b, z - c), (x - a, y - b, z - c), (x + a, y - b, z - c)
            ), "bottom", self.mat),
            Plane((
                (x - a, y - b, z - c), (x - a, y + b, z - c), (x - a, y + b, z + c)
            ), "left", self.mat),
            Plane((
                (x + a, y + b, z - c), (x + a, y - b, z - c), (x + a, y - b, z + c)
            ), "right", self.mat),
            Plane((
                (x - a, y + b, z - c), (x + a, y + b, z - c), (x + a, y + b, z + c)
            ), "front", self.mat),
            Plane((
                (x + a, y - b, z - c), (x - a, y - b, z - c), (x - a, y - b, z + c)
            ), "back", self.mat),
        ]

        return planes

    def __repr__(self):
        return """solid
	{
		"id" "2"
		%s
	} """ % ("\n".join([str(p) for p in self.planes]))


class Event():

    def __init__(self, event_name="", target_name="", trigger_event_name="", param_override="", delay=0):
        self.t_name = target_name
        self.e_name = event_name
        self.t_e_name = trigger_event_name
        self.param_override = param_override
        self.delay = delay

    def __repr__(self):
        return "\"%s\" \"%s%s%s%s%s\"" % (self.e_name, self.t_name, self.t_e_name, self.param_override, self.delay, "-1")


class Entity():
    ids = {
        "prop_button": "362",
        "scripted_sequence": "339",
        "info_player_start": "8",
        "prop_portal": "471",
    }
    entity_count = 0

    def __init__(self, origin=(0, 0, 0), angles=(0, 0, 0), type="", name=""):
        self.origin = origin
        self.type = type
        self.name = name
        self.angles = angles

        Entity.entity_count += 1

    def get_entity_string(self):
        return self.__repr__()

    def __repr__(self):
        return """
entity
{{
	"id" "%s"
	"classname" "%s"
	"angles" "%s"
	"targetname" "%s"
	"origin" "%s"
	{extras}
}}""" % (
            Entity.ids[self.type],
            self.type,
            " ".join(str(c) for c in self.angles),
            self.name,
            " ".join(str(c) for c in self.origin)
        )


class EntityPlayer():
    _type = "entity"

    def __init__(self, origin=(0, 0, 0), angles=(0, 0, 0)):
        self.e = Entity(origin=origin, angles=angles, type="info_player_start")

    def __repr__(self):
        return str(self.e).format(extras="")


class EntityButton():
    _type = "entity"

    def __init__(self, origin=(0, 0, 0), angles=(0, 0, 0), events=None):
        self.e = Entity(origin=origin, angles=angles, type="prop_button",
                        name="prop_button_%s" % Entity.entity_count)
        self.events = events

    def __repr__(self):
        return str(self.e).format(extras="""
	"Delay" "1"
	"istimer" "0"
	"preventfastreset" "0"
	"skin" "0"
	connections
	{
		%s
	}""" % ("\n".join(str(e) if(e is not None) else "" for e in self.events)))


class EntityScriptedSequence():
    _type = "entity"

    def __init__(self, origin=(0, 0, 0), name="", events=None):
        self.e = Entity(origin=origin, type="scripted_sequence",
                        name=name)
        self.events = events

    def __repr__(self):
        return str(self.e).format(extras="""
	"disableX360" "0"
	"m_bDisableNPCCollisions" "0"
	"m_bIgnoreGravity" "0"
	"m_bLoopActionSequence" "0"
	"m_bSynchPostIdles" "0"
	"m_flRadius" "0"
	"m_flRepeat" "0"
	"m_fMoveTo" "1"
	"maxcpulevel" "0"
	"maxgpulevel" "0"
	"mincpulevel" "0"
	"mingpulevel" "0"
	"onplayerdeath" "0"
	"spawnflags" "0"
	connections
	{
		%s
	}""" % ("\n".join(str(e) if(e is not None) else "" for e in self.events)))


class EntityAutoPortal():
    _type = "entity"

    portal_count = 0

    def __init__(self, origin=(0, 0, 0), name="", colour=""):
        self.count = Entity.entity_count
        self.colour = colour

        # self.portal_frame = Entity(
        #     origin=origin, type="prop_static", angles=(-90, 90, 0))
        self.portal = Entity(origin=(origin[0] - 7, origin[1] - 3, origin[2] / 2), type="prop_portal",
                             angles=(-90, 90, 0), name=name)
        # self.relay = Entity(origin=origin, type="logic_relay",
        #                     name=name)

        EntityAutoPortal.portal_count += 1

    def __repr__(self):
        return "%s" % (
            str(self.portal).format(extras="""
    "Activated" "0"
	"HalfHeight" "0"
	"HalfWidth" "0"
	"LinkageGroupID" "-1"
	"PortalTwo" "%s"
			""" % self.colour)
        )


class VMFFile():
    content = """world
{{
	"id" "1"
	"mapversion" "6"
	"classname" "worldspawn"
	"detailmaterial" "detail/detailsprites"
	"detailvbsp" "detail.vbsp"
	"maxblobcount" "250"
	"maxpropscreenwidth" "-1"
	"skyname" "sky_black_nofog"
	{solids}
}}
{entities}"""

    def __init__(self, path="/"):
        self.p = path

        self.solids = []
        self.entities = []

    def append(self, any):
        if(any._type == "solid"):
            self.solids.append(any)
        elif(any._type == "entity"):
            self.entities.append(any)
        else:
            raise Exception("Unknown type %s" % type(any))

    def write_to_file(self, name):
        path = Path(self.p) / Path(name)

        with open(path, "w") as f:
            f.write(
                VMFFile.content.format(
                    solids=("".join(str(x) for x in self.solids)),
                    entities=("".join(str(x) for x in self.entities)),
                )
            )
