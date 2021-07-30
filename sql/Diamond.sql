Update FTNodes
set FTNodes.RecNum = DD.FT_RecNum, FTNodes.RecType = DD.FT_RecType, FTNodes.Transfer=-1
From
(
    select
    Events.ID,
    BE_FTNodes.RecNum as BE_RecNum,
    BE_FTNodes.RecType as BE_RecType,
    FT_FTNodes.RecNum as FT_RecNum,
    FT_FTNodes.RecType as FT_RecType
    from Events
    JOIN FT ON Events.ID=FT.ID
    JOIN FTNodes as BE_FTNodes ON Events.Num=BE_FTNodes.RecNum and Events.Type=BE_FTNodes.RecType
    JOIN FTNodes as FT_FTNodes  ON FT.Num=FT_FTNodes.FTNum
    where Events.Type=5 AND Events.Symbol=2 AND Events.Tag=-1 AND FT_FTNodes.FatherGateNum=0
) as DD
where FTNodes.RecNum = DD.BE_RecNum and FTNodes.RecType = DD.BE_RecType