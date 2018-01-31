#!/usr/bin/env python

from netaddr import IPSet

Register = dict


class MatchFailedException(Exception):
    pass


class MatchIntersectException(Exception):
    pass


class Match():
    """
    A header field map. Each header field includes a prefix value.
    """

    def __init__(self, src_ip=None, dst_ip=None, src_port=None, dst_port=None, protocol=None, register_checker={}):
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.protocol = protocol
        self.register_checker = register_checker

    def __eq__(self, other):
        if type(other) is not Match:
            return False
        if self.src_ip == other.src_ip and self.dst_ip == other.dst_ip and self.src_port == other.dst_port and \
                self.dst_port == other.dst_port and self.protocol == other.protocol and \
                self.register_checker == other.register_checker:
            return True
        return False

    def __repr__(self):
        return str(self.to_dict())

    def __hash__(self):
        return hash(self.to_tuple())

    def to_tuple(self):
        return (self.src_ip, self.dst_ip, self.src_port, self.dst_port,
                self.protocol, tuple(self.register_checker.items()))

    def to_dict(self):
        return {
            "src-ip": self.src_ip,
            "dst-ip": self.dst_ip,
            "src-port": self.src_port,
            "dst-port": self.dst_port,
            "protocol": self.protocol,
            "register-checker": self.register_checker
        }

    @staticmethod
    def from_dict(match_dict):
        return Match(src_ip=match_dict.get('src-ip', None),
                     dst_ip=match_dict.get('dst-ip', None),
                     src_port=match_dict.get('src-port', None),
                     dst_port=match_dict.get('dst-port', None),
                     protocol=match_dict.get('protocol', None),
                     register_checker=match_dict.get('register-checker', {}))

    def intersect(self, other):
        # type: (Match) -> Match|None
        try:
            return self._intersect(other)
        except MatchIntersectException:
            return None

    def _intersect(self, other):
        # type: (Match) -> Match

        # if port and protocol mismatch, fail
        if (self.src_port is not None and other.src_port is not None and self.src_port != other.src_port) or \
                (self.dst_port is not None and other.dst_port is not None and self.dst_port != other.dst_port) or \
                (self.protocol is not None and other.protocol is not None and self.protocol != other.protocol):
            raise MatchIntersectException

        intersect_src_port = self.src_port or other.src_port
        intersect_dst_port = self.dst_port or other.dst_port
        intersect_protocol = self.protocol or other.protocol

        if self.src_ip is None or other.src_ip is None:
            intersect_src_ip = self.src_ip or other.src_ip
        else:
            try:
                intersect_src_ip = str((IPSet([self.src_ip]) & IPSet([other.src_ip])).iter_cidrs()[0])
            except IndexError:
                raise MatchIntersectException

        if self.dst_ip is None or other.dst_ip is None:
            intersect_dst_ip = self.dst_ip or other.dst_ip
        else:
            try:
                intersect_dst_ip = str((IPSet([self.dst_ip]) & IPSet([other.dst_ip])).iter_cidrs()[0])
            except IndexError:
                raise MatchIntersectException

        # if register checker cannot be merged, fail
        merged_register_checker = self.register_checker
        for checker in merged_register_checker:
            if checker in other.register_checker.keys() and \
                    other.register_checker[checker] != merged_register_checker[checker]:
                raise MatchIntersectException
            merged_register_checker[checker] = other.register_checker[checker]

        # try to find intersection of ip prefixes
        try:
            match = Match(
                src_ip=intersect_src_ip,
                dst_ip=intersect_dst_ip,
                src_port=intersect_src_port,
                dst_port=intersect_dst_port,
                protocol=intersect_protocol,
                register_checker=merged_register_checker
            )
        except IndexError:
            raise MatchIntersectException
        return match

    def intersect_list(self, match_list):
        # type: (list[Match]) -> Match
        result = self
        try:
            for match in match_list:
                result = result._intersect(match)
        except MatchIntersectException:
            result = None
        return result

    def compare(self):
        pass

    def to_header_space(self):
        pass

    def match(self, pkt, register):
        # type: (Packet, Register) -> bool

        # Judge the values in register
        for key in self.register_checker:
            value = self.register_checker[key]
            if register[key] != value:
                return False

        if self.src_ip and pkt.src_ip not in IPSet([self.src_ip]):
            return False
        if self.dst_ip and pkt.dst_ip not in IPSet([self.dst_ip]):
            return False
        if self.src_port and pkt.src_port != self.src_port:
            return False
        if self.dst_port and pkt.dst_port != self.dst_port:
            return False
        if self.protocol and pkt.protocol != self.protocol:
            return False

        return True


class Packet():
    def __init__(self, src_ip, dst_ip, src_port, dst_port, protocol):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol

    def to_match(self):
        return Match()


class FlowSpace():
    """
    Flow Space
    """

    def __init__(self, matches=None):
        self.matches = matches or set()
        assert type(self.matches) == set

    def __contains__(self, match):
        if type(match) != Match:
            return False
        else:
            return match in self.matches

    def intersect(self, match):
        """
        Return a subspace which matches match.
        """
        intersection = set()
        for m in self.matches:
            intersection.add(m.intersect(match))
        return FlowSpace(intersection)
