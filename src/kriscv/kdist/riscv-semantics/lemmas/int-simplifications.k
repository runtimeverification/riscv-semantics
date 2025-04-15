module INT-SIMPLIFICATIONS [symbolic]
    imports INT
    imports K-EQUAL
    imports BOOL

    rule A:Int |Int B:Int ==K C:Int |Int D:Int => A ==K C andBool B ==K D [simplification]
    rule A:Int <<Int B:Int ==K C:Int <<Int D:Int => A ==K C andBool B ==K D [simplification]
    
endmodule