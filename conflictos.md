Usando el sistema de torneos suizos pueden ocurrir empates entre los jugadores con mayor puntaje.
La idea es jugar una cantidad de rondas tal que rondas = top(log2(E)) siendo E la cantidad de equipos, esto
nos garantiza que haya a lo sumo un equipo sin partidos perdidos, por ende a lo sumo un ganador. Pero
puede pasar que no haya equipo sin partidos perdidos.

En el caso de tener una cantidad de equipos potencia de dos al final de la cantidad ideal de rondas
tenemos un unico ganador.

En el caso de tener una cantidad de equipos no potencia de dos podemos tener que en la ultima ronda el
equipo top pierda y ganen los equipos que tenian 1 punto menos que el top. Y asi quedar con varios
equipos empatados. __Este es el caso que queremos resolver__

Como resolvemos el caso del empate entre los equipos con mas puntos?
Las formas mas populares tienen en cuenta a quienes se han enfrentado anteriormente, a mi me parece
que es dificil de convencer a el publico que eso es un metodo justo pero es algo a discutir.

