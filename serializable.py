from abc import ABC

class Serializable(ABC):

    def to_dict(self):
        
        # Öffentliche Methode, um das Objekt zu serialisieren.
        return self.__to_dict()

    def __to_dict(self, *args):

        # Wenn kein Argument übergeben wurde, bei 'self' anfragen
        if len(args) > 0:
            obj = args[0]
        else:
            obj = self

        if isinstance(obj, dict):
            # Dictionary: Werte rekursiv umwandeln
            data = {}
            for (k, v) in obj.items():
                data[k] = self.__to_dict(v)
            return data
            
        elif hasattr(obj, "__iter__") and not isinstance(obj, str):
            # Listen/Sets (aber keine Strings): Elemente rekursiv umwandeln
            data = [self.__to_dict(v) for v in obj]
            return data
            
        elif hasattr(obj, "__dict__"):
            # Objekte mit Attributen: __dict__ auslesen und rekursiv umwandeln
            data = []
            for k, v in obj.__dict__.items():
                # Private Attribute überspringen wir ggf., 
                # oder wir nehmen alles mit. Hier nehmen wir alles:
                data.append((k, self.__to_dict(v)))
            return dict(data)
            
        else:
            # Basistypen (int, str, float, datetime) einfach zurückgeben
            # Das DateTime-Handling übernimmt dann der DatabaseConnector
            return obj