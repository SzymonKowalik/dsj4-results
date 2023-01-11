# DSJ4-rankings
This program allows to create additional competitions for DSJ4 World Cup as well as provide
every competition results, tournament classification, jumper and team competition history.
You can choose if competition ranking will be based on points or note as well as include 
qualification or individual note from team competition to ranking. Application is based 
on flask web server with sqlite integration.

## Customising calendar
Calendar options are placed in `./data/planned_calendar.txt` file.\
Each competition must be written in new line in format `{hill_name};{type}`.\
Type is either `'ind'` or `'team'`.\
Hill name and type are separated by semicolon.\
For example:
```
Lillehammer HS140;ind
Vikersund HS240;ind
Vikersund HS240;team
```

## Customising tournaments
Tournament options are placed in `./data/tournaments.txt` file.\
Each tournament must be written in new line in format\
`{name};{type};{competition_ids};{qualification_ids}`
* name - name of tournament
* type - 0 for points | 1 for notes
* competition_ids - comma separated ids of competition
* qualification_ids (optional) - comma separated ids of qualifications

For example:
```
RawAir;1;1,2,3,4,5;1,2,3,4
Four Hills Tournament;1;11,12,13,14
Ski Flying Cup;0;4,15,16,19,21
```

*Team competition will not work with point type tournaments.\
Competitors will be rewarded 0 points.

## Requirements
* Python 3
* The required packages are listed in `requirements.txt`.
* DSJ4 Stats folder (C:\Users\\{user}\Documents\Deluxe Ski Jump 4)
